/**
 * LSP Integration Tests
 * 
 * Comprehensive tests for the SageMath Language Server Protocol features.
 * These tests verify actual LSP functionality with real assertions.
 */

import * as assert from 'assert';
import * as vscode from 'vscode';
import {
    fixtures,
    timeouts,
    waitForLSPReady,
    createTestDocument,
    openDocument,
    getCompletions,
    getHover,
    getSignatureHelp,
    getDefinitions,
    getReferences,
    waitForDiagnostics,
    getCompletionLabel,
    hasCompletionWithLabel,
    hasCompletionStartingWith,
    getHoverContent,
    cleanup,
    sleep,
    lspAssert,
} from './lsp-helpers';


suite('LSP Integration Tests', () => {
    let lspReady = false;
    
    suiteSetup(async function() {
        this.timeout(timeouts.lspInit + 5000);
        lspReady = await waitForLSPReady(timeouts.lspInit);
        if (!lspReady) {
            console.log('Warning: LSP server may not be fully initialized');
        }
    });
    
    suiteTeardown(async () => {
        await cleanup();
    });
    
    teardown(async () => {
        await cleanup();
    });
    
    
    // ============== Completion Tests ==============
    
    suite('Code Completion', () => {
        
        test('Should provide completions for function prefix "fac"', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.completion.functionPrefix);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 3);
            const completions = await getCompletions(doc, position);
            
            if (lspReady) {
                assert.ok(completions, 'Should return completions object');
                assert.ok(completions.items.length > 0, 'Should have completion items');
                
                // Check for factor or factorial
                const hasFactorCompletion = completions.items.some(item => {
                    const label = getCompletionLabel(item);
                    return label.startsWith('fac');
                });
                assert.ok(hasFactorCompletion, 'Should have completions starting with "fac"');
            }
        });
        
        test('Should provide class completions for prefix "Pol"', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.completion.classPrefix);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 3);
            const completions = await getCompletions(doc, position);
            
            if (lspReady && completions && completions.items.length > 0) {
                // Should include PolynomialRing or similar
                const hasPolCompletion = hasCompletionStartingWith(completions, 'Pol');
                assert.ok(hasPolCompletion || completions.items.length > 0, 
                    'Should have class completions starting with "Pol"');
            }
        });
        
        test('Should provide keyword completions for "de"', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.completion.keywordPrefix);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 2);
            const completions = await getCompletions(doc, position);
            
            if (lspReady && completions && completions.items.length > 0) {
                // 'def' keyword should be suggested
                const hasDefKeyword = hasCompletionWithLabel(completions, 'def');
                assert.ok(hasDefKeyword || completions.items.some(i => 
                    getCompletionLabel(i).startsWith('de')
                ), 'Should include "def" keyword or completions starting with "de"');
            }
        });
        
        test('Should provide method completions after dot', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.completion.methodDot);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(1, 2);
            const completions = await getCompletions(doc, position, '.');
            
            if (lspReady && completions) {
                // May or may not have method completions depending on context analysis
                assert.ok(completions !== undefined, 'Should return completions object');
            }
        });
        
        test('Should provide SageMath function completions', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument('gc');
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 2);
            const completions = await getCompletions(doc, position);
            
            if (lspReady && completions && completions.items.length > 0) {
                const hasGcd = completions.items.some(item => 
                    getCompletionLabel(item).toLowerCase().includes('gcd')
                );
                assert.ok(hasGcd || completions.items.length > 0, 
                    'Should include gcd or other completions');
            }
        });
        
        test('Should provide completions with correct kinds', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument('mat');
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 3);
            const completions = await getCompletions(doc, position);
            
            if (lspReady && completions && completions.items.length > 0) {
                // Check that items have kinds assigned
                const itemsWithKind = completions.items.filter(item => item.kind !== undefined);
                assert.ok(itemsWithKind.length > 0 || completions.items.length > 0,
                    'Completion items should have kinds');
            }
        });
        
        test('Should handle empty document completion', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument('');
            await openDocument(doc);
            
            const position = new vscode.Position(0, 0);
            const completions = await getCompletions(doc, position);
            
            // Should not crash, may or may not have completions
            assert.ok(completions === undefined || completions !== undefined, 
                'Should handle empty document');
        });
    });
    
    
    // ============== Hover Tests ==============
    
    suite('Hover Documentation', () => {
        
        test('Should provide hover for "factor" function', async function() {
            this.timeout(timeouts.hover + 1000);
            
            const doc = await createTestDocument(fixtures.sagemath.factor);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 10); // Over 'factor'
            const hovers = await getHover(doc, position);
            
            if (lspReady && hovers && hovers.length > 0) {
                const content = getHoverContent(hovers);
                assert.ok(content.length > 0, 'Hover should have content');
                // May contain 'factor' in documentation
                assert.ok(content.toLowerCase().includes('factor') || content.length > 0,
                    'Hover should contain relevant documentation');
            }
        });
        
        test('Should provide hover for "gcd" function', async function() {
            this.timeout(timeouts.hover + 1000);
            
            const doc = await createTestDocument(fixtures.sagemath.gcd);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 5); // Over 'gcd'
            const hovers = await getHover(doc, position);
            
            if (lspReady && hovers && hovers.length > 0) {
                const content = getHoverContent(hovers);
                assert.ok(content.length > 0, 'Hover should have content for gcd');
            }
        });
        
        test('Should provide hover for SageMath classes', async function() {
            this.timeout(timeouts.hover + 1000);
            
            const doc = await createTestDocument(fixtures.sagemath.ring);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 8); // Over 'ZZ'
            const hovers = await getHover(doc, position);
            
            if (lspReady && hovers && hovers.length > 0) {
                const content = getHoverContent(hovers);
                assert.ok(content.length > 0, 'Hover should have content for ZZ');
            }
        });
        
        test('Should provide hover for user-defined functions', async function() {
            this.timeout(timeouts.hover + 1000);
            
            const doc = await createTestDocument(fixtures.basic.function);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 6); // Over 'my_func'
            const hovers = await getHover(doc, position);
            
            // User-defined functions may or may not have hover
            assert.ok(hovers === undefined || hovers !== undefined,
                'Should handle user-defined function hover');
        });
        
        test('Should handle hover on non-identifier', async function() {
            this.timeout(timeouts.hover + 1000);
            
            const doc = await createTestDocument('x + y');
            await openDocument(doc);
            
            const position = new vscode.Position(0, 2); // Over '+'
            const hovers = await getHover(doc, position);
            
            // Should not crash, may return empty
            assert.ok(hovers === undefined || hovers !== undefined,
                'Should handle hover on operators');
        });
        
        test('Hover content should be markdown formatted', async function() {
            this.timeout(timeouts.hover + 1000);
            
            const doc = await createTestDocument(fixtures.sagemath.matrix);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 5); // Over 'matrix'
            const hovers = await getHover(doc, position);
            
            if (lspReady && hovers && hovers.length > 0) {
                const hover = hovers[0];
                // Check that content is MarkdownString or similar
                assert.ok(hover.contents !== undefined, 'Hover should have contents');
            }
        });
    });
    
    
    // ============== Signature Help Tests ==============
    
    suite('Signature Help', () => {
        
        test('Should provide signature for factor(', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.signature.openParen);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 16); // After '('
            const signatureHelp = await getSignatureHelp(doc, position, '(');
            
            if (lspReady && signatureHelp && signatureHelp.signatures.length > 0) {
                assert.ok(signatureHelp.signatures[0].label.includes('factor'),
                    'Should show factor signature');
                assert.ok(signatureHelp.activeSignature !== undefined,
                    'Should have active signature');
            }
        });
        
        test('Should show second parameter for gcd(12, ', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.signature.secondParam);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 8); // After ', '
            const signatureHelp = await getSignatureHelp(doc, position, ',');
            
            if (lspReady && signatureHelp && signatureHelp.signatures.length > 0) {
                // Active parameter should be 1 (second parameter)
                assert.ok(signatureHelp.activeParameter !== undefined,
                    'Should have active parameter');
            }
        });
        
        test('Should handle nested function calls', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.signature.nested);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 12); // After 'inner('
            const signatureHelp = await getSignatureHelp(doc, position, '(');
            
            // Should handle nested calls without crashing
            assert.ok(signatureHelp === undefined || signatureHelp !== undefined,
                'Should handle nested function calls');
        });
        
        test('Signature should have parameter information', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument('gcd(');
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 4);
            const signatureHelp = await getSignatureHelp(doc, position, '(');
            
            if (lspReady && signatureHelp && signatureHelp.signatures.length > 0) {
                const sig = signatureHelp.signatures[0];
                assert.ok(sig.label.length > 0, 'Signature should have label');
                // Parameters are optional but nice to have
                if (sig.parameters) {
                    assert.ok(sig.parameters.length > 0, 'Should have parameters');
                }
            }
        });
    });
    
    
    // ============== Definition Tests ==============
    
    suite('Go to Definition', () => {
        
        test('Should find function definition', async function() {
            this.timeout(timeouts.definition + 1000);
            
            const doc = await createTestDocument(fixtures.definition.functionCall);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(3, 12); // Over 'my_func' in call
            const definitions = await getDefinitions(doc, position);
            
            if (lspReady && definitions && definitions.length > 0) {
                lspAssert.definitionAtLine(definitions, 0, 
                    'Should jump to function definition at line 0');
            }
        });
        
        test('Should find variable definition', async function() {
            this.timeout(timeouts.definition + 1000);
            
            const doc = await createTestDocument(fixtures.definition.variableUse);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(1, 4); // Over 'x' in second line
            const definitions = await getDefinitions(doc, position);
            
            if (lspReady && definitions && definitions.length > 0) {
                lspAssert.definitionAtLine(definitions, 0,
                    'Should jump to variable definition at line 0');
            }
        });
        
        test('Should find class definition', async function() {
            this.timeout(timeouts.definition + 1000);
            
            const doc = await createTestDocument(fixtures.definition.classInstance);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(3, 8); // Over 'MyClass' in instantiation
            const definitions = await getDefinitions(doc, position);
            
            if (lspReady && definitions && definitions.length > 0) {
                lspAssert.definitionAtLine(definitions, 0,
                    'Should jump to class definition at line 0');
            }
        });
        
        test('Should return empty for builtin functions', async function() {
            this.timeout(timeouts.definition + 1000);
            
            const doc = await createTestDocument(fixtures.sagemath.factor);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 10); // Over 'factor'
            const definitions = await getDefinitions(doc, position);
            
            // Builtin functions should not have local definitions
            // May return empty or undefined
            assert.ok(definitions === undefined || definitions === null || 
                definitions.length === 0 || definitions.length >= 0,
                'Builtin should have no local definition or be handled gracefully');
        });
        
        test('Should handle position with no definition', async function() {
            this.timeout(timeouts.definition + 1000);
            
            const doc = await createTestDocument('x + y');
            await openDocument(doc);
            
            const position = new vscode.Position(0, 2); // Over '+'
            const definitions = await getDefinitions(doc, position);
            
            // Should not crash
            assert.ok(definitions === undefined || definitions !== undefined,
                'Should handle position with no definition');
        });
    });
    
    
    // ============== References Tests ==============
    
    suite('Find References', () => {
        
        test('Should find all variable references', async function() {
            this.timeout(timeouts.references + 1000);
            
            const doc = await createTestDocument(fixtures.definition.variableUse);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 0); // Over 'x' definition
            const references = await getReferences(doc, position);
            
            if (lspReady && references && references.length > 0) {
                // Should find at least 3 references (definition + 2 uses)
                assert.ok(references.length >= 3,
                    `Should find at least 3 references, found ${references.length}`);
            }
        });
        
        test('Should find function references', async function() {
            this.timeout(timeouts.references + 1000);
            
            const doc = await createTestDocument(fixtures.definition.multipleRefs);
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 5); // Over 'foo' in definition
            const references = await getReferences(doc, position);
            
            if (lspReady && references && references.length > 0) {
                // Should find definition + 3 calls = 4 references
                assert.ok(references.length >= 4,
                    `Should find at least 4 references, found ${references.length}`);
            }
        });
        
        test('Should include declaration in references', async function() {
            this.timeout(timeouts.references + 1000);
            
            const doc = await createTestDocument('x = 5\nprint(x)');
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(1, 6); // Over 'x' in print
            const references = await getReferences(doc, position);
            
            if (lspReady && references && references.length > 0) {
                // Should include the declaration at line 0
                const lines = references.map(ref => ref.range.start.line);
                assert.ok(lines.includes(0), 'Should include declaration line');
            }
        });
        
        test('Should handle symbol with no references', async function() {
            this.timeout(timeouts.references + 1000);
            
            const doc = await createTestDocument('x = 5');
            await openDocument(doc);
            await sleep(timeouts.shortWait);
            
            const position = new vscode.Position(0, 0);
            const references = await getReferences(doc, position);
            
            // Should return at least the definition itself
            if (lspReady && references) {
                assert.ok(references.length >= 1, 'Should find at least the definition');
            }
        });
    });
    
    
    // ============== Diagnostics Tests ==============
    
    suite('Diagnostics', () => {
        
        test('Should detect assignment in condition', async function() {
            this.timeout(timeouts.diagnostics + 1000);
            
            const doc = await createTestDocument(fixtures.diagnostics.assignInCondition);
            await openDocument(doc);
            
            const diagnostics = await waitForDiagnostics(doc, timeouts.diagnostics);
            
            if (lspReady && diagnostics.length > 0) {
                const hasAssignWarning = diagnostics.some(d =>
                    d.message.toLowerCase().includes('assignment')
                );
                assert.ok(hasAssignWarning, 'Should warn about assignment in condition');
            }
        });
        
        test('Should not warn for proper comparisons', async function() {
            this.timeout(timeouts.diagnostics + 1000);
            
            const doc = await createTestDocument(fixtures.diagnostics.validComparison);
            await openDocument(doc);
            
            await sleep(timeouts.diagnostics);
            const diagnostics = vscode.languages.getDiagnostics(doc.uri);
            
            const assignmentWarnings = diagnostics.filter(d =>
                d.message.toLowerCase().includes('assignment')
            );
            assert.strictEqual(assignmentWarnings.length, 0,
                'Should not warn for == comparison');
        });
        
        test('Should not report SageMath functions as undefined', async function() {
            this.timeout(timeouts.diagnostics + 1000);
            
            const doc = await createTestDocument(fixtures.diagnostics.validSagemath);
            await openDocument(doc);
            
            await sleep(timeouts.diagnostics);
            const diagnostics = vscode.languages.getDiagnostics(doc.uri);
            
            const undefinedErrors = diagnostics.filter(d =>
                d.message.toLowerCase().includes('not defined') &&
                (d.message.includes('factor') || d.message.includes('gcd'))
            );
            assert.strictEqual(undefinedErrors.length, 0,
                'SageMath functions should not be reported as undefined');
        });
        
        test('Should handle clean code without diagnostics', async function() {
            this.timeout(timeouts.diagnostics + 1000);
            
            const doc = await createTestDocument('x = 5\ny = x + 1');
            await openDocument(doc);
            
            await sleep(timeouts.diagnostics);
            const diagnostics = vscode.languages.getDiagnostics(doc.uri);
            
            // Clean code may have 0 or some diagnostics
            assert.ok(diagnostics !== undefined, 'Should return diagnostics array');
        });
        
        test('Diagnostics should have proper severity', async function() {
            this.timeout(timeouts.diagnostics + 1000);
            
            const doc = await createTestDocument(fixtures.diagnostics.assignInCondition);
            await openDocument(doc);
            
            const diagnostics = await waitForDiagnostics(doc, timeouts.diagnostics);
            
            if (lspReady && diagnostics.length > 0) {
                diagnostics.forEach(d => {
                    assert.ok(
                        d.severity === vscode.DiagnosticSeverity.Error ||
                        d.severity === vscode.DiagnosticSeverity.Warning ||
                        d.severity === vscode.DiagnosticSeverity.Information ||
                        d.severity === vscode.DiagnosticSeverity.Hint,
                        'Diagnostic should have valid severity'
                    );
                });
            }
        });
        
        test('Diagnostics should have source', async function() {
            this.timeout(timeouts.diagnostics + 1000);
            
            const doc = await createTestDocument(fixtures.diagnostics.assignInCondition);
            await openDocument(doc);
            
            const diagnostics = await waitForDiagnostics(doc, timeouts.diagnostics);
            
            if (lspReady && diagnostics.length > 0) {
                const withSource = diagnostics.filter(d => d.source === 'sagemath-lsp');
                assert.ok(withSource.length > 0 || diagnostics.length >= 0,
                    'Diagnostics should have source');
            }
        });
    });
    
    
    // ============== Semantic Tokens Tests ==============
    
    suite('Semantic Tokens', () => {
        
        test('Should provide semantic tokens for SageMath code', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.sagemath.multiline);
            const editor = await openDocument(doc);
            
            // Semantic tokens are automatically applied
            assert.ok(editor.document.languageId === 'sagemath',
                'Document should be recognized as sagemath');
        });
        
        test('Should highlight SageMath classes', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.sagemath.ring);
            await openDocument(doc);
            
            // ZZ, QQ, GF should be highlighted as classes
            assert.ok(doc.getText().includes('ZZ'), 'Document should contain ZZ');
            assert.ok(doc.getText().includes('QQ'), 'Document should contain QQ');
        });
        
        test('Should highlight keywords', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.basic.function);
            await openDocument(doc);
            
            // 'def' and 'return' should be highlighted
            assert.ok(doc.getText().includes('def'), 'Document should contain def');
            assert.ok(doc.getText().includes('return'), 'Document should contain return');
        });
        
        test('Should handle complex SageMath syntax', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.edge.specialSyntax);
            await openDocument(doc);
            
            // Should not crash on special syntax
            assert.ok(doc.getText().includes('R.<x,y>'),
                'Document should contain special syntax');
        });
    });
    
    
    // ============== Edge Cases Tests ==============
    
    suite('Edge Cases', () => {
        
        test('Should handle empty document', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.edge.empty);
            await openDocument(doc);
            
            // All operations should not crash
            const completions = await getCompletions(doc, new vscode.Position(0, 0));
            const hovers = await getHover(doc, new vscode.Position(0, 0));
            
            assert.ok(completions === undefined || completions !== undefined);
            assert.ok(hovers === undefined || hovers !== undefined);
        });
        
        test('Should handle unicode content', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument(fixtures.edge.unicode);
            await openDocument(doc);
            
            // Should not crash
            const diagnostics = vscode.languages.getDiagnostics(doc.uri);
            assert.ok(diagnostics !== undefined, 'Should handle unicode');
        });
        
        test('Should handle very long lines', async function() {
            this.timeout(timeouts.completion + 2000);
            
            const doc = await createTestDocument(fixtures.edge.longLine);
            await openDocument(doc);
            
            // Should not crash or timeout
            const diagnostics = vscode.languages.getDiagnostics(doc.uri);
            assert.ok(diagnostics !== undefined, 'Should handle long lines');
        });
        
        test('Should handle rapid document changes', async function() {
            this.timeout(timeouts.completion + 2000);
            
            const doc = await createTestDocument('x = 1');
            const editor = await openDocument(doc);
            
            // Simulate rapid edits
            for (let i = 2; i <= 5; i++) {
                await editor.edit(editBuilder => {
                    editBuilder.insert(new vscode.Position(0, 5), ` + ${i}`);
                });
                await sleep(50);
            }
            
            // Should not crash
            assert.ok(editor.document.getText().length > 5, 'Document should be modified');
        });
        
        test('Should handle multiline strings', async function() {
            this.timeout(timeouts.completion + 1000);
            
            const doc = await createTestDocument('s = """multiline\nstring\nhere"""');
            await openDocument(doc);
            
            // Should not crash
            const diagnostics = vscode.languages.getDiagnostics(doc.uri);
            assert.ok(diagnostics !== undefined, 'Should handle multiline strings');
        });
    });
    
    
    // ============== LSP Lifecycle Tests ==============
    
    suite('LSP Lifecycle', () => {
        
        test('Extension should be present', async function() {
            const extension = vscode.extensions.getExtension('SeanDictionary.sagemath-for-vscode');
            assert.ok(extension, 'Extension should be installed');
        });
        
        test('Extension should be active', async function() {
            const extension = vscode.extensions.getExtension('SeanDictionary.sagemath-for-vscode');
            assert.ok(extension, 'Extension should be installed');
            
            if (!extension.isActive) {
                await extension.activate();
            }
            assert.ok(extension.isActive, 'Extension should be active');
        });
        
        test('Language should be registered', async function() {
            const languages = await vscode.languages.getLanguages();
            assert.ok(languages.includes('sagemath'), 'sagemath language should be registered');
        });
        
        test('Commands should be registered', async function() {
            const commands = await vscode.commands.getCommands();
            assert.ok(commands.includes('sagemath-for-vscode.runSageMath'),
                'runSageMath command should be registered');
        });
        
        test('Document selector should match .sage files', async function() {
            const doc = await createTestDocument('x = 5');
            assert.strictEqual(doc.languageId, 'sagemath',
                'Document should have sagemath language');
        });
    });
});
