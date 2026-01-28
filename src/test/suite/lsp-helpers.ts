/**
 * LSP Test Helper Utilities
 * 
 * Provides helper functions and fixtures for testing LSP functionality
 * in the SageMath VS Code extension.
 */

import * as vscode from 'vscode';

/**
 * Test fixtures for SageMath code samples
 */
export const fixtures = {
    // Basic SageMath code
    basic: {
        variable: 'x = 5',
        assignment: 'x = 5\ny = x + 1',
        function: 'def my_func(x):\n    return x * 2',
        classdef: 'class MyClass:\n    def __init__(self):\n        self.value = 0',
    },
    
    // SageMath-specific code
    sagemath: {
        factor: 'result = factor(120)',
        gcd: 'g = gcd(12, 18)',
        matrix: 'M = matrix(ZZ, 2, 2, [1, 2, 3, 4])',
        polynomial: "R.<x> = PolynomialRing(QQ)\np = x^2 + 2*x + 1",
        ring: 'ring = ZZ\nfield = QQ\ngf = GF(101)',
        multiline: 'def compute():\n    a = factor(100)\n    b = gcd(12, 18)\n    return a, b',
    },
    
    // Completion test code
    completion: {
        functionPrefix: 'fac',
        classPrefix: 'Pol',
        keywordPrefix: 'de',
        methodDot: 'M = matrix(ZZ, 2, 2)\nM.',
        afterImport: 'from sage.all import ',
    },
    
    // Definition/reference test code
    definition: {
        functionCall: 'def my_func(x):\n    return x * 2\n\nresult = my_func(5)',
        variableUse: 'x = 5\ny = x + 1\nz = x * 2',
        classInstance: 'class MyClass:\n    pass\n\nobj = MyClass()',
        multipleRefs: 'def foo():\n    return 1\n\na = foo()\nb = foo()\nc = foo()',
    },
    
    // Diagnostic test code
    diagnostics: {
        mixedIndent: 'def foo():\n\t x = 5',  // Tab followed by space
        assignInCondition: 'if x = 5:\n    print(x)',
        validComparison: 'if x == 5:\n    print(x)',
        undefinedCall: 'result = unknown_function()',
        validSagemath: 'result = factor(120)\nx = gcd(12, 18)',
    },
    
    // Signature help test code
    signature: {
        openParen: 'result = factor(',
        secondParam: 'gcd(12, ',
        nested: 'outer(inner(',
        multiParam: 'matrix(ZZ, 2, 2, ',
    },
    
    // Edge cases
    edge: {
        empty: '',
        unicode: 'π = 3.14159\n∑ = sum([1,2,3])',
        longLine: 'x = ' + '1 + '.repeat(100) + '1',
        specialSyntax: 'R.<x,y> = PolynomialRing(QQ)',
    }
};

/**
 * Configuration for waiting timeouts
 */
export const timeouts = {
    lspInit: 5000,        // Wait for LSP to initialize
    completion: 2000,     // Wait for completions
    hover: 1000,          // Wait for hover
    diagnostics: 2000,    // Wait for diagnostics
    definition: 1000,     // Wait for definition
    references: 1000,     // Wait for references
    shortWait: 500,       // Short wait for UI updates
};

/**
 * Wait for the LSP server to be ready
 */
export async function waitForLSPReady(timeout: number = timeouts.lspInit): Promise<boolean> {
    const extension = vscode.extensions.getExtension('SeanDictionary.sagemath-for-vscode');
    
    if (!extension) {
        console.log('Extension not found');
        return false;
    }
    
    if (!extension.isActive) {
        await extension.activate();
    }
    
    // Wait for LSP to initialize
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
        // Try to get a simple completion to check if LSP is ready
        try {
            const doc = await vscode.workspace.openTextDocument({
                language: 'sagemath',
                content: 'x'
            });
            
            const completions = await vscode.commands.executeCommand<vscode.CompletionList>(
                'vscode.executeCompletionItemProvider',
                doc.uri,
                new vscode.Position(0, 1)
            );
            
            // Close the test document
            await vscode.commands.executeCommand('workbench.action.closeActiveEditor');
            
            if (completions && completions.items.length > 0) {
                return true;
            }
        } catch {
            // Ignore errors, LSP not ready yet
        }
        
        await sleep(500);
    }
    
    return false;
}

/**
 * Create a test document with given content
 */
export async function createTestDocument(
    content: string,
    language: string = 'sagemath'
): Promise<vscode.TextDocument> {
    return await vscode.workspace.openTextDocument({
        language,
        content
    });
}

/**
 * Open a document in the editor
 */
export async function openDocument(doc: vscode.TextDocument): Promise<vscode.TextEditor> {
    return await vscode.window.showTextDocument(doc);
}

/**
 * Get completions at a position
 */
export async function getCompletions(
    doc: vscode.TextDocument,
    position: vscode.Position,
    triggerChar?: string
): Promise<vscode.CompletionList | undefined> {
    return await vscode.commands.executeCommand<vscode.CompletionList>(
        'vscode.executeCompletionItemProvider',
        doc.uri,
        position,
        triggerChar
    );
}

/**
 * Get hover information at a position
 */
export async function getHover(
    doc: vscode.TextDocument,
    position: vscode.Position
): Promise<vscode.Hover[] | undefined> {
    return await vscode.commands.executeCommand<vscode.Hover[]>(
        'vscode.executeHoverProvider',
        doc.uri,
        position
    );
}

/**
 * Get signature help at a position
 */
export async function getSignatureHelp(
    doc: vscode.TextDocument,
    position: vscode.Position,
    triggerChar?: string
): Promise<vscode.SignatureHelp | undefined> {
    return await vscode.commands.executeCommand<vscode.SignatureHelp>(
        'vscode.executeSignatureHelpProvider',
        doc.uri,
        position,
        triggerChar
    );
}

/**
 * Get definitions at a position
 */
export async function getDefinitions(
    doc: vscode.TextDocument,
    position: vscode.Position
): Promise<vscode.Location[] | vscode.LocationLink[] | undefined> {
    return await vscode.commands.executeCommand<vscode.Location[] | vscode.LocationLink[]>(
        'vscode.executeDefinitionProvider',
        doc.uri,
        position
    );
}

/**
 * Get references at a position
 */
export async function getReferences(
    doc: vscode.TextDocument,
    position: vscode.Position
): Promise<vscode.Location[] | undefined> {
    return await vscode.commands.executeCommand<vscode.Location[]>(
        'vscode.executeReferenceProvider',
        doc.uri,
        position
    );
}

/**
 * Get diagnostics for a document
 */
export function getDiagnostics(doc: vscode.TextDocument): vscode.Diagnostic[] {
    return vscode.languages.getDiagnostics(doc.uri);
}

/**
 * Wait for diagnostics to be published
 */
export async function waitForDiagnostics(
    doc: vscode.TextDocument,
    timeout: number = timeouts.diagnostics
): Promise<vscode.Diagnostic[]> {
    return new Promise((resolve) => {
        const startTime = Date.now();
        
        const checkDiagnostics = () => {
            const diagnostics = getDiagnostics(doc);
            if (diagnostics.length > 0 || Date.now() - startTime > timeout) {
                resolve(diagnostics);
            } else {
                setTimeout(checkDiagnostics, 100);
            }
        };
        
        checkDiagnostics();
    });
}

/**
 * Extract label from completion item
 */
export function getCompletionLabel(item: vscode.CompletionItem): string {
    return typeof item.label === 'string' ? item.label : item.label.label;
}

/**
 * Check if completions contain an item with given label
 */
export function hasCompletionWithLabel(
    completions: vscode.CompletionList | undefined,
    label: string
): boolean {
    if (!completions || !completions.items) {
        return false;
    }
    return completions.items.some(item => getCompletionLabel(item) === label);
}

/**
 * Check if completions contain an item starting with prefix
 */
export function hasCompletionStartingWith(
    completions: vscode.CompletionList | undefined,
    prefix: string
): boolean {
    if (!completions || !completions.items) {
        return false;
    }
    return completions.items.some(item => getCompletionLabel(item).startsWith(prefix));
}

/**
 * Check if completions contain an item of given kind
 */
export function hasCompletionOfKind(
    completions: vscode.CompletionList | undefined,
    kind: vscode.CompletionItemKind
): boolean {
    if (!completions || !completions.items) {
        return false;
    }
    return completions.items.some(item => item.kind === kind);
}

/**
 * Extract hover content as string
 */
export function getHoverContent(hovers: vscode.Hover[] | undefined): string {
    if (!hovers || hovers.length === 0) {
        return '';
    }
    
    const contents = hovers[0].contents;
    if (Array.isArray(contents)) {
        return contents.map(c => {
            if (typeof c === 'string') {
                return c;
            }
            if (typeof c === 'object' && c !== null && 'value' in c) {
                return (c as vscode.MarkdownString).value;
            }
            return '';
        }).join('\n');
    }
    
    if (typeof contents === 'string') {
        return contents;
    }
    
    if (typeof contents === 'object' && contents !== null && 'value' in contents) {
        return (contents as vscode.MarkdownString).value;
    }
    
    return '';
}

/**
 * Sleep utility
 */
export function sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Clean up test documents
 */
export async function cleanup(): Promise<void> {
    await vscode.commands.executeCommand('workbench.action.closeAllEditors');
}

/**
 * Assert helper for LSP tests
 */
export const lspAssert = {
    /**
     * Assert completions are available
     */
    hasCompletions(
        completions: vscode.CompletionList | undefined,
        message?: string
    ): void {
        if (!completions || completions.items.length === 0) {
            throw new Error(message || 'Expected completions but got none');
        }
    },
    
    /**
     * Assert specific completion exists
     */
    hasCompletion(
        completions: vscode.CompletionList | undefined,
        label: string,
        message?: string
    ): void {
        if (!hasCompletionWithLabel(completions, label)) {
            const available = completions?.items.map(i => getCompletionLabel(i)).join(', ') || 'none';
            throw new Error(message || `Expected completion '${label}' but not found. Available: ${available}`);
        }
    },
    
    /**
     * Assert hover has content
     */
    hasHoverContent(
        hovers: vscode.Hover[] | undefined,
        message?: string
    ): void {
        const content = getHoverContent(hovers);
        if (!content) {
            throw new Error(message || 'Expected hover content but got none');
        }
    },
    
    /**
     * Assert hover contains text
     */
    hoverContains(
        hovers: vscode.Hover[] | undefined,
        text: string,
        message?: string
    ): void {
        const content = getHoverContent(hovers);
        if (!content.includes(text)) {
            throw new Error(message || `Expected hover to contain '${text}' but got: ${content}`);
        }
    },
    
    /**
     * Assert signature help is available
     */
    hasSignature(
        signatureHelp: vscode.SignatureHelp | undefined,
        message?: string
    ): void {
        if (!signatureHelp || signatureHelp.signatures.length === 0) {
            throw new Error(message || 'Expected signature help but got none');
        }
    },
    
    /**
     * Assert definitions found
     */
    hasDefinitions(
        definitions: vscode.Location[] | vscode.LocationLink[] | undefined,
        message?: string
    ): void {
        if (!definitions || definitions.length === 0) {
            throw new Error(message || 'Expected definitions but got none');
        }
    },
    
    /**
     * Assert definition at specific line
     */
    definitionAtLine(
        definitions: vscode.Location[] | vscode.LocationLink[] | undefined,
        line: number,
        message?: string
    ): void {
        if (!definitions || definitions.length === 0) {
            throw new Error(message || 'No definitions found');
        }
        
        const firstDef = definitions[0];
        const defLine = 'targetRange' in firstDef 
            ? firstDef.targetRange.start.line 
            : firstDef.range.start.line;
        
        if (defLine !== line) {
            throw new Error(message || `Expected definition at line ${line} but got line ${defLine}`);
        }
    },
    
    /**
     * Assert references count
     */
    hasReferencesCount(
        references: vscode.Location[] | undefined,
        count: number,
        message?: string
    ): void {
        const actual = references?.length || 0;
        if (actual < count) {
            throw new Error(message || `Expected at least ${count} references but got ${actual}`);
        }
    },
    
    /**
     * Assert diagnostic exists with message containing text
     */
    hasDiagnosticContaining(
        diagnostics: vscode.Diagnostic[],
        text: string,
        message?: string
    ): void {
        const found = diagnostics.some(d => d.message.toLowerCase().includes(text.toLowerCase()));
        if (!found) {
            const messages = diagnostics.map(d => d.message).join(', ') || 'none';
            throw new Error(message || `Expected diagnostic containing '${text}' but got: ${messages}`);
        }
    },
    
    /**
     * Assert no diagnostic with message containing text
     */
    noDiagnosticContaining(
        diagnostics: vscode.Diagnostic[],
        text: string,
        message?: string
    ): void {
        const found = diagnostics.find(d => d.message.toLowerCase().includes(text.toLowerCase()));
        if (found) {
            throw new Error(message || `Expected no diagnostic containing '${text}' but found: ${found.message}`);
        }
    }
};
