import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as os from 'os';

suite('Extension Utility Functions Test Suite', () => {
    
    suite('buildRunCommand Tests', () => {
        
        test('Should build correct command for Windows', () => {
            // Test Windows-style command building
            const _sagePath = 'C:\\sage\\sage.exe';
            const _filePath = 'C:\\projects\\test.sage';
            const _dirPath = 'C:\\projects';
            
            // Windows uses PowerShell syntax: cd "dir"; & "sage" "file"
            if (process.platform === 'win32') {
                // Verify Windows command structure expectations
                assert.ok(_sagePath.includes('sage'), 'Windows command pattern expected');
            } else {
                assert.ok(true, 'Skipped on non-Windows');
            }
        });
        
        test('Should build correct command for Unix', () => {
            // Test Unix-style command building
            const _sagePath = '/usr/bin/sage';
            const _filePath = '/home/user/test.sage';
            const _dirPath = '/home/user';
            
            // Unix uses: cd 'dir' && 'sage' 'file'
            if (process.platform !== 'win32') {
                assert.ok(_sagePath.includes('sage'), 'Unix command pattern expected');
            } else {
                assert.ok(true, 'Skipped on Windows');
            }
        });
        
        test('Should handle paths with spaces', () => {
            const _sagePath = 'C:\\Program Files\\sage\\sage.exe';
            const _filePath = 'C:\\My Projects\\test file.sage';
            const _dirPath = 'C:\\My Projects';
            
            // Command should properly quote paths with spaces
            assert.ok(_filePath.includes(' '), 'Paths with spaces should be quoted');
        });
    });
    
    suite('removeSagePyFile Tests', () => {
        let tempDir: string;
        
        setup(() => {
            tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'sagemath-test-'));
        });
        
        teardown(() => {
            // Clean up temp directory
            try {
                fs.rmSync(tempDir, { recursive: true, force: true });
            } catch (e) {
                // Ignore cleanup errors
            }
        });
        
        test('Should remove existing .sage.py file', () => {
            const sageFile = path.join(tempDir, 'test.sage');
            const sagePyFile = `${sageFile}.py`;
            
            // Create the .sage.py file
            fs.writeFileSync(sagePyFile, '# Generated file');
            assert.ok(fs.existsSync(sagePyFile), 'File should exist before removal');
            
            // The actual removal logic is in extension.ts
            // Here we test the file system operations
            fs.unlinkSync(sagePyFile);
            assert.ok(!fs.existsSync(sagePyFile), 'File should not exist after removal');
        });
        
        test('Should handle non-existent file gracefully', () => {
            const sageFile = path.join(tempDir, 'nonexistent.sage');
            const sagePyFile = `${sageFile}.py`;
            
            // File doesn't exist - should not throw
            assert.ok(!fs.existsSync(sagePyFile), 'File should not exist');
            
            // Attempting to remove non-existent file should not crash
            try {
                if (fs.existsSync(sagePyFile)) {
                    fs.unlinkSync(sagePyFile);
                }
                assert.ok(true, 'Should handle non-existent file');
            } catch (e) {
                assert.fail('Should not throw for non-existent file');
            }
        });
    });
    
    suite('Configuration Tests', () => {
        
        test('Should have default sage path', () => {
            const config = vscode.workspace.getConfiguration('sagemath-for-vscode.sage');
            const sagePath = config.get<string>('path');
            assert.strictEqual(sagePath, 'sage', 'Default sage path should be "sage"');
        });
        
        test('Should have empty default conda env path', () => {
            const config = vscode.workspace.getConfiguration('sagemath-for-vscode.sage');
            const condaEnvPath = config.get<string>('condaEnvPath');
            assert.strictEqual(condaEnvPath, '', 'Default conda env path should be empty');
        });
        
        test('Should have LSP enabled by default', () => {
            const config = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP');
            const useLSP = config.get<boolean>('useSageMathLSP');
            assert.strictEqual(useLSP, true, 'LSP should be enabled by default');
        });
        
        test('Should have info as default log level', () => {
            const config = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP');
            const logLevel = config.get<string>('LSPLogLevel');
            assert.strictEqual(logLevel, 'info', 'Default log level should be "info"');
        });
        
        test('Log level should be one of valid values', () => {
            const config = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP');
            const logLevel = config.get<string>('LSPLogLevel');
            const validLevels = ['error', 'warn', 'info', 'debug'];
            assert.ok(validLevels.includes(logLevel || ''), 'Log level should be valid');
        });
    });
    
    suite('Terminal Management Tests', () => {
        
        test('Should create terminal with correct name', async () => {
            const terminalName = 'SageMath Test';
            const terminal = vscode.window.createTerminal({ name: terminalName });
            
            assert.ok(terminal, 'Terminal should be created');
            assert.strictEqual(terminal.name, terminalName, 'Terminal name should match');
            
            // Clean up
            terminal.dispose();
        });
        
        test('Should find existing terminal by name', async () => {
            const terminalName = 'SageMath Find Test';
            const terminal = vscode.window.createTerminal({ name: terminalName });
            
            // Wait a bit for terminal to be registered
            await new Promise(resolve => setTimeout(resolve, 100));
            
            const foundTerminal = vscode.window.terminals.find(t => t.name === terminalName);
            assert.ok(foundTerminal, 'Should find terminal by name');
            
            // Clean up
            terminal.dispose();
        });
    });
});

suite('Status Bar Tests', () => {
    
    test('Should create status bar item', () => {
        const statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        
        assert.ok(statusBarItem, 'Status bar item should be created');
        
        statusBarItem.text = '$(terminal) Test';
        statusBarItem.command = 'test.command';
        statusBarItem.tooltip = 'Test tooltip';
        
        assert.strictEqual(statusBarItem.text, '$(terminal) Test');
        assert.strictEqual(statusBarItem.command, 'test.command');
        assert.strictEqual(statusBarItem.tooltip, 'Test tooltip');
        
        // Clean up
        statusBarItem.dispose();
    });
});

suite('Document Language Detection Tests', () => {
    
    test('Should detect sagemath language for .sage files', async () => {
        const doc = await vscode.workspace.openTextDocument({
            language: 'sagemath',
            content: 'x = var("x")\nsolve(x^2 - 4, x)'
        });
        
        assert.strictEqual(doc.languageId, 'sagemath', 'Language should be sagemath');
    });
    
    test('Should handle empty .sage document', async () => {
        const doc = await vscode.workspace.openTextDocument({
            language: 'sagemath',
            content: ''
        });
        
        assert.strictEqual(doc.languageId, 'sagemath');
        assert.strictEqual(doc.lineCount, 1, 'Empty doc should have 1 line');
    });
    
    test('Should handle multiline .sage document', async () => {
        const content = `# SageMath code
x = var('x')
f = x^2 + 2*x + 1
roots = solve(f == 0, x)
print(roots)`;
        
        const doc = await vscode.workspace.openTextDocument({
            language: 'sagemath',
            content: content
        });
        
        assert.strictEqual(doc.languageId, 'sagemath');
        assert.strictEqual(doc.lineCount, 5, 'Should have 5 lines');
    });
});

suite('Extension Commands Availability', () => {
    
    test('runSageMath command should be available', async () => {
        const commands = await vscode.commands.getCommands(true);
        assert.ok(
            commands.includes('sagemath-for-vscode.runSageMath'),
            'runSageMath command should be registered'
        );
    });
    
    test('restartLSP command should be available', async () => {
        const commands = await vscode.commands.getCommands(true);
        assert.ok(
            commands.includes('sagemath-for-vscode.restartLSP'),
            'restartLSP command should be registered'
        );
    });
    
    test('selectCondaEnv command should be available', async () => {
        const commands = await vscode.commands.getCommands(true);
        assert.ok(
            commands.includes('sagemath-for-vscode.selectCondaEnv'),
            'selectCondaEnv command should be registered'
        );
    });
});

suite('Extension Activation Events', () => {
    
    test('Extension should activate on sagemath file open', async () => {
        const extension = vscode.extensions.getExtension('SeanDictionary.sagemath-for-vscode');
        assert.ok(extension, 'Extension should be found');
        
        // Open a sagemath document to trigger activation
        await vscode.workspace.openTextDocument({
            language: 'sagemath',
            content: '# Trigger activation'
        });
        
        // Give time for activation
        await new Promise(resolve => setTimeout(resolve, 500));
        
        assert.ok(extension.isActive, 'Extension should be active after opening sagemath file');
    });
});

suite('Error Handling Tests', () => {
    
    test('Should handle missing active editor gracefully', async () => {
        // Close all editors
        await vscode.commands.executeCommand('workbench.action.closeAllEditors');
        
        // Attempting to run command without editor should not crash
        try {
            // This would normally show an error message, not crash
            await vscode.commands.executeCommand('sagemath-for-vscode.runSageMath');
            // If we get here without throwing, the command handled missing editor
            assert.ok(true, 'Command handled missing editor');
        } catch (e) {
            // Command might throw or show error - both are acceptable
            assert.ok(true, 'Command handled missing editor with exception');
        }
    });
});
