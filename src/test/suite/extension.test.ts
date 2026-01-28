import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');

    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('SeanDictionary.sagemath-for-vscode'));
    });

    test('Extension should activate', async () => {
        const extension = vscode.extensions.getExtension('SeanDictionary.sagemath-for-vscode');
        assert.ok(extension);
        
        if (extension && !extension.isActive) {
            await extension.activate();
        }
        assert.ok(extension?.isActive);
    });

    test('Commands should be registered', async () => {
        const commands = await vscode.commands.getCommands(true);
        
        assert.ok(commands.includes('sagemath-for-vscode.runSageMath'), 
            'runSageMath command should be registered');
        assert.ok(commands.includes('sagemath-for-vscode.restartLSP'), 
            'restartLSP command should be registered');
        assert.ok(commands.includes('sagemath-for-vscode.selectCondaEnv'), 
            'selectCondaEnv command should be registered');
        assert.ok(commands.includes('sagemath-for-vscode.setupWizard'), 
            'setupWizard command should be registered');
        assert.ok(commands.includes('sagemath-for-vscode.checkSageStatus'), 
            'checkSageStatus command should be registered');
        assert.ok(commands.includes('sagemath-for-vscode.discoverSage'), 
            'discoverSage command should be registered');
        assert.ok(commands.includes('sagemath-for-vscode.showInstallGuide'), 
            'showInstallGuide command should be registered');
    });

    test('Language configuration should be registered', () => {
        const languages = vscode.languages.getLanguages();
        languages.then((langs) => {
            assert.ok(langs.includes('sagemath'), 'SageMath language should be registered');
        });
    });

    test('Configuration settings should exist', () => {
        const config = vscode.workspace.getConfiguration('sagemath-for-vscode');
        
        assert.notStrictEqual(config.get('sage.path'), undefined, 
            'sage.path setting should exist');
        assert.notStrictEqual(config.get('sage.condaEnvPath'), undefined, 
            'sage.condaEnvPath setting should exist');
        assert.notStrictEqual(config.get('LSP.useSageMathLSP'), undefined, 
            'LSP.useSageMathLSP setting should exist');
        assert.notStrictEqual(config.get('LSP.LSPLogLevel'), undefined, 
            'LSP.LSPLogLevel setting should exist');
    });
});

suite('SageMath Language Support', () => {
    test('Should recognize .sage file extension', async () => {
        const doc = await vscode.workspace.openTextDocument({
            language: 'sagemath',
            content: '# SageMath test file\nprint("Hello, SageMath!")'
        });
        
        assert.strictEqual(doc.languageId, 'sagemath');
    });
});
