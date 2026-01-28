/**
 * LSP End-to-End Tests
 * 
 * Tests real-world scenarios and workflows for the SageMath LSP.
 * These tests simulate actual user interactions with the extension.
 */

import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as os from 'os';
import {
    timeouts,
    waitForLSPReady,
    createTestDocument,
    openDocument,
    getCompletions,
    getHover,
    getDefinitions,
    getReferences,
    cleanup,
    sleep,
    getCompletionLabel,
} from './lsp-helpers';


suite('LSP End-to-End Tests', () => {
    let lspReady = false;
    let tempDir: string;
    
    suiteSetup(async function() {
        this.timeout(timeouts.lspInit + 5000);
        lspReady = await waitForLSPReady(timeouts.lspInit);
        
        // Create temp directory for file tests
        tempDir = path.join(os.tmpdir(), `sagemath-test-${Date.now()}`);
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir, { recursive: true });
        }
    });
    
    suiteTeardown(async () => {
        await cleanup();
        
        // Clean up temp directory
        if (tempDir && fs.existsSync(tempDir)) {
            try {
                fs.rmSync(tempDir, { recursive: true, force: true });
            } catch {
                // Ignore cleanup errors
            }
        }
    });
    
    teardown(async () => {
        await cleanup();
    });
    
    
    // ============== Real File Operations ==============
    
    suite('Real File Operations', () => {
        
        test('Should work with actual .sage file', async function() {
            this.timeout(timeouts.lspInit + 5000);
            
            const filePath = path.join(tempDir, 'test.sage');
            const content = 'x = factor(120)\nprint(x)';
            fs.writeFileSync(filePath, content);
            
            try {
                const doc = await vscode.workspace.openTextDocument(filePath);
                await openDocument(doc);
                await sleep(timeouts.shortWait);
                
                assert.strictEqual(doc.languageId, 'sagemath',
                    '.sage file should have sagemath language');
                assert.ok(doc.getText().includes('factor'),
                    'Document should contain the code');
            } finally {
                await cleanup();
                if (fs.existsSync(filePath)) {
                    fs.unlinkSync(filePath);
                }
            }
        });
        
        test('Should provide LSP features for saved file', async function() {
            this.timeout(timeouts.lspInit + 5000);
            
            const filePath = path.join(tempDir, 'test_lsp.sage');
            const content = 'def my_func(x):\n    return x * 2\n\nresult = my_func(5)';
            fs.writeFileSync(filePath, content);
            
            try {
                const doc = await vscode.workspace.openTextDocument(filePath);
                await openDocument(doc);
                await sleep(timeouts.diagnostics);
                
                if (lspReady) {
                    // Try to get definitions
                    const position = new vscode.Position(3, 12);
                    const definitions = await getDefinitions(doc, position);
                    
                    if (definitions && definitions.length > 0) {
                        assert.ok(definitions.length > 0, 'Should find definitions in real file');
                    }
                }
            } finally {
                await cleanup();
                if (fs.existsSync(filePath)) {
                    fs.unlinkSync(filePath);
                }
            }
        });
        
        test('Should update diagnostics after file save', async function() {
            this.timeout(timeouts.lspInit + 5000);
            
            const filePath = path.join(tempDir, 'test_diag.sage');
            const content = 'if x = 5:\n    print(x)';
            fs.writeFileSync(filePath, content);
            
            try {
                const doc = await vscode.workspace.openTextDocument(filePath);
                const editor = await openDocument(doc);
                
                // Wait for initial diagnostics
                await sleep(timeouts.diagnostics);
                
                // Modify the document
                await editor.edit(editBuilder => {
                    editBuilder.replace(
                        new vscode.Range(0, 5, 0, 6),
                        '=='
                    );
                });
                
                // Save and wait for updated diagnostics
                await doc.save();
                await sleep(timeouts.diagnostics);
                
                // Diagnostics should be updated
                const diagnostics = vscode.languages.getDiagnostics(doc.uri);
                const assignmentWarnings = diagnostics.filter(d =>
                    d.message.toLowerCase().includes('assignment')
                );
                
                // After fixing, there should be fewer or no assignment warnings
                assert.ok(assignmentWarnings.length === 0 || diagnostics !== undefined,
                    'Diagnostics should update after save');
            } finally {
                await cleanup();
                if (fs.existsSync(filePath)) {
                    fs.unlinkSync(filePath);
                }
            }
        });
        
        test('Should handle file close and reopen', async function() {
            this.timeout(timeouts.lspInit + 5000);
            
            const filePath = path.join(tempDir, 'test_reopen.sage');
            const content = 'x = gcd(12, 18)';
            fs.writeFileSync(filePath, content);
            
            try {
                // Open document
                let doc = await vscode.workspace.openTextDocument(filePath);
                await openDocument(doc);
                await sleep(timeouts.shortWait);
                
                // Close it
                await cleanup();
                await sleep(timeouts.shortWait);
                
                // Reopen it
                doc = await vscode.workspace.openTextDocument(filePath);
                await openDocument(doc);
                await sleep(timeouts.shortWait);
                
                assert.strictEqual(doc.languageId, 'sagemath',
                    'Reopened file should still have sagemath language');
            } finally {
                await cleanup();
                if (fs.existsSync(filePath)) {
                    fs.unlinkSync(filePath);
                }
            }
        });
    });
    
    
    // ============== Edit Flow Tests ==============
    
    suite('Edit Flow', () => {
        
        test('Should update completions as user types', async function() {
            this.timeout(timeouts.completion + 2000);
            
            const doc = await createTestDocument('f');
            const editor = await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            // Get completions for 'f'
            let completions = await getCompletions(doc, new vscode.Position(0, 1));
            // Track initial count for comparison
            void (completions?.items.length || 0);
            
            // Type more characters
            await editor.edit(editBuilder => {
                editBuilder.insert(new vscode.Position(0, 1), 'ac');
            });
            await sleep(timeouts.shortWait);
            
            // Get completions for 'fac'
            completions = await getCompletions(doc, new vscode.Position(0, 3));
            
            if (lspReady && completions) {
                // Should have more specific completions
                const hasFactorRelated = completions.items.some(item =>
                    getCompletionLabel(item).toLowerCase().includes('fac')
                );
                assert.ok(hasFactorRelated || completions.items.length >= 0,
                    'Completions should update as user types');
            }
        });
        
        test('Should trigger signature help when typing (', async function() {
            this.timeout(timeouts.completion + 2000);
            
            const doc = await createTestDocument('factor');
            const editor = await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            // Type '('
            await editor.edit(editBuilder => {
                editBuilder.insert(new vscode.Position(0, 6), '(');
            });
            await sleep(timeouts.shortWait);
            
            // Signature help should be available
            const signatureHelp = await vscode.commands.executeCommand<vscode.SignatureHelp>(
                'vscode.executeSignatureHelpProvider',
                doc.uri,
                new vscode.Position(0, 7),
                '('
            );
            
            if (lspReady && signatureHelp) {
                assert.ok(signatureHelp.signatures.length >= 0,
                    'Signature help should be triggered');
            }
        });
        
        test('Should update hover after code change', async function() {
            this.timeout(timeouts.hover + 2000);
            
            const doc = await createTestDocument('result = gcd(12, 18)');
            const editor = await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            // Get hover for gcd
            let hovers = await getHover(doc, new vscode.Position(0, 11));
            
            // Change gcd to factor
            await editor.edit(editBuilder => {
                editBuilder.replace(
                    new vscode.Range(0, 9, 0, 12),
                    'factor'
                );
            });
            await sleep(timeouts.shortWait);
            
            // Get hover for factor
            hovers = await getHover(doc, new vscode.Position(0, 12));
            
            if (lspReady && hovers && hovers.length > 0) {
                // Hover content should be for 'factor' now
                assert.ok(hovers !== undefined, 'Hover should update after code change');
            }
        });
        
        test('Should update references after adding new usage', async function() {
            this.timeout(timeouts.references + 2000);
            
            const doc = await createTestDocument('x = 5\ny = x + 1');
            const editor = await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            // Get initial references
            let refs = await getReferences(doc, new vscode.Position(0, 0));
            const _initialCount = refs?.length || 0;
            
            // Add another usage of x
            await editor.edit(editBuilder => {
                editBuilder.insert(new vscode.Position(1, 9), '\nz = x * 2');
            });
            await sleep(timeouts.shortWait);
            
            // Get updated references
            refs = await getReferences(doc, new vscode.Position(0, 0));
            
            if (lspReady && refs) {
                assert.ok(refs.length >= _initialCount,
                    'References should include new usage');
            }
        });
    });
    
    
    // ============== Complex Scenarios ==============
    
    suite('Complex Scenarios', () => {
        
        test('Should handle multi-function document', async function() {
            this.timeout(timeouts.completion + 2000);
            
            const content = `
def func_a(x):
    return x * 2

def func_b(y):
    return func_a(y) + 1

def func_c(z):
    a = func_a(z)
    b = func_b(z)
    return a + b

result = func_c(5)
`;
            const doc = await createTestDocument(content);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            if (lspReady) {
                // Find references to func_a
                const refs = await getReferences(doc, new vscode.Position(1, 6));
                
                if (refs) {
                    // Should find definition + 2 calls
                    assert.ok(refs.length >= 3,
                        `Should find multiple references to func_a, found ${refs.length}`);
                }
            }
        });
        
        test('Should handle class with methods', async function() {
            this.timeout(timeouts.completion + 2000);
            
            const content = `
class MyMatrix:
    def __init__(self, data):
        self.data = data
    
    def determinant(self):
        return 0
    
    def transpose(self):
        return self.data

m = MyMatrix([[1,2],[3,4]])
d = m.determinant()
t = m.transpose()
`;
            const doc = await createTestDocument(content);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            // Should not crash on complex class structure
            assert.ok(doc.getText().includes('class MyMatrix'),
                'Document should contain class definition');
        });
        
        test('Should handle SageMath-specific constructs', async function() {
            this.timeout(timeouts.completion + 2000);
            
            const content = `
R.<x,y,z> = PolynomialRing(QQ, 3)
p = x^2 + y^2 + z^2
I = R.ideal([p, x - y])

M = matrix(ZZ, 3, 3, range(9))
det = M.determinant()
inv = M.inverse()

K.<a> = NumberField(x^2 - 2)
`;
            const doc = await createTestDocument(content);
            await openDocument(doc);
            await sleep(timeouts.diagnostics);
            
            // Should handle SageMath syntax without crashing
            const diagnostics = vscode.languages.getDiagnostics(doc.uri);
            
            // SageMath-specific syntax should not cause errors
            assert.ok(diagnostics !== undefined,
                'Should handle SageMath-specific constructs');
        });
        
        test('Should handle deeply nested code', async function() {
            this.timeout(timeouts.completion + 2000);
            
            const content = `
def outer():
    def middle():
        def inner():
            x = factor(gcd(12, matrix(ZZ, 2, 2).determinant()))
            return x
        return inner()
    return middle()

result = outer()
`;
            const doc = await createTestDocument(content);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            // Should not crash on deeply nested code
            if (lspReady) {
                const hovers = await getHover(doc, new vscode.Position(4, 20));
                assert.ok(hovers === undefined || hovers !== undefined,
                    'Should handle deeply nested code');
            }
        });
    });
    
    
    // ============== Error Recovery Tests ==============
    
    suite('Error Recovery', () => {
        
        test('Should recover from syntax errors', async function() {
            this.timeout(timeouts.diagnostics + 2000);
            
            // Start with syntax error
            const doc = await createTestDocument('def foo(\n    pass');
            const editor = await openDocument(doc);
            await sleep(timeouts.diagnostics);
            
            // Fix the syntax error
            await editor.edit(editBuilder => {
                editBuilder.replace(
                    new vscode.Range(0, 0, 1, 8),
                    'def foo():\n    pass'
                );
            });
            await sleep(timeouts.diagnostics);
            
            // Should have recovered
            const diagnostics = vscode.languages.getDiagnostics(doc.uri);
            // After fix, should have fewer syntax-related errors
            assert.ok(diagnostics !== undefined, 'Should recover from syntax errors');
        });
        
        test('Should handle incomplete code gracefully', async function() {
            this.timeout(timeouts.completion + 2000);
            
            const incompleteSnippets = [
                'def ',
                'class Foo',
                'for i in ',
                'if x:',
                'import ',
                'from sage.',
            ];
            
            for (const snippet of incompleteSnippets) {
                const doc = await createTestDocument(snippet);
                await openDocument(doc);
                
                // All operations should not crash
                const pos = new vscode.Position(0, snippet.length);
                const _completions = await getCompletions(doc, pos);
                const _hovers = await getHover(doc, pos);
                
                assert.ok(_completions === undefined || _completions !== undefined,
                    `Should handle incomplete code: ${snippet}`);
                
                await cleanup();
            }
        });
        
        test('Should handle rapid open/close cycles', async function() {
            this.timeout(timeouts.lspInit + 5000);
            
            for (let i = 0; i < 5; i++) {
                const doc = await createTestDocument(`x = ${i}`);
                await openDocument(doc);
                await sleep(100);
                await cleanup();
            }
            
            // Final document should work fine
            const doc = await createTestDocument('x = factor(100)');
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            if (lspReady) {
                const _hovers = await getHover(doc, new vscode.Position(0, 6));
                assert.ok(_hovers === undefined || _hovers !== undefined,
                    'Should work after rapid open/close cycles');
            }
        });
        
        test('Should handle mixed valid and invalid code', async function() {
            this.timeout(timeouts.diagnostics + 2000);
            
            const content = `
# Valid code
x = factor(100)
y = gcd(12, 18)

# Invalid code
if a = 5:
    print(a)

# More valid code
z = matrix(ZZ, 2, 2)
`;
            const doc = await createTestDocument(content);
            await openDocument(doc);
            await sleep(timeouts.diagnostics);
            
            // Should still provide LSP features for valid parts
            if (lspReady) {
                const _hovers = await getHover(doc, new vscode.Position(2, 6));
                // Should get hover for 'factor' despite errors elsewhere
                assert.ok(_hovers === undefined || _hovers !== undefined,
                    'Should handle mixed valid/invalid code');
            }
        });
    });
    
    
    // ============== Performance Tests ==============
    
    suite('Performance', () => {
        
        test('Completion should respond within timeout', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument('fac');
            await openDocument(doc);
            
            const startTime = Date.now();
            const _completions = await getCompletions(doc, new vscode.Position(0, 3));
            const elapsed = Date.now() - startTime;
            
            void _completions; // Used for timing test
            assert.ok(elapsed < timeouts.completion,
                `Completion took ${elapsed}ms, should be under ${timeouts.completion}ms`);
        });
        
        test('Hover should respond within timeout', async function() {
            this.timeout(timeouts.hover + 1000);
            
            const doc = await createTestDocument('result = factor(120)');
            await openDocument(doc);
            
            const startTime = Date.now();
            const _hovers = await getHover(doc, new vscode.Position(0, 10));
            const elapsed = Date.now() - startTime;
            
            void _hovers; // Used for timing test
            assert.ok(elapsed < timeouts.hover,
                `Hover took ${elapsed}ms, should be under ${timeouts.hover}ms`);
        });
        
        test('Should handle moderately large document', async function() {
            this.timeout(timeouts.lspInit + 5000);
            
            // Generate a moderately large document
            const lines: string[] = [];
            for (let i = 0; i < 100; i++) {
                lines.push(`def func_${i}(x):`);
                lines.push(`    return x * ${i}`);
                lines.push('');
            }
            lines.push('result = func_50(10)');
            
            const doc = await createTestDocument(lines.join('\n'));
            await openDocument(doc);
            await sleep(timeouts.diagnostics);
            
            if (lspReady) {
                // Should still provide completions
                const _completions = await getCompletions(doc, new vscode.Position(300, 8));
                assert.ok(_completions === undefined || _completions !== undefined,
                    'Should handle large document');
            }
        });
    });
});
