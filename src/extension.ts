import * as vscode from 'vscode';
import { basename, join, dirname } from 'path';
import { existsSync, rmSync, unlinkSync } from 'fs';
import { exec } from 'child_process';
import {
    runSetupWizard,
    checkSageStatus,
    discoverSageInstallations,
    getInstallationGuide,
    validateSagePath
} from './sageDiscovery';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind,
    State as ClientState
} from 'vscode-languageclient/node';

let client: LanguageClient;
let isLSPStarted = false;

// ============== Utility Functions ==============

/**
 * Get list of available Conda environments
 */
function getCondaEnvs(): Promise<{ name: string; path: string }[]> {
    return new Promise((resolve, reject) => {
        exec('conda env list --json', (error, stdout, stderr) => {
            if (error) {
                reject(new Error(`Get Conda Envs Error: ${stderr}`));
                return;
            }
            const envs: { name: string; path: string }[] = [];

            try {
                const data = JSON.parse(stdout);
                if (data.envs) {
                    data.envs.forEach((envPath: string) => {
                        const envName = basename(envPath);
                        envs.push({ name: envName, path: envPath });
                    });
                }
            } catch (parseError) {
                reject(new Error(`Parse Conda Envs Error: ${parseError}`));
                return;
            }
            resolve(envs);
        });
    });
}

/**
 * Install Python requirements in the specified environment
 */
function installRequirements(envLSPpath: string, requirementsPath: string): Promise<void> {
    return new Promise((resolve, reject) => {
        const pipPath = process.platform === 'win32'
            ? join(envLSPpath, 'Scripts', 'pip.exe')
            : join(envLSPpath, 'bin', 'pip');
        exec(`"${pipPath}" install -r "${requirementsPath}"`, (error, stdout, stderr) => {
            if (error) {
                reject(new Error(`Install Requirements Error: ${stderr}`));
                return;
            }
            resolve();
        });
    });
}

/**
 * Create Python venv for LSP server
 */
async function createEnvLSP(
    envLSPpath: string,
    requirementsPath: string,
    condaEnvPath: string | undefined
): Promise<void> {
    if (!condaEnvPath) {
        throw new Error('Conda environment path is required to create LSP venv');
    }

    const sagePythonPath = process.platform === 'win32'
        ? join(condaEnvPath, 'Scripts', 'sage')
        : join(condaEnvPath, 'bin', 'sage');

    return new Promise((resolve, reject) => {
        exec(`"${sagePythonPath}" -python -m venv "${envLSPpath}"`, (error, stdout, stderr) => {
            if (error) {
                reject(new Error(`Create venv Error: ${error.message}`));
                return;
            }

            installRequirements(envLSPpath, requirementsPath)
                .then(() => resolve())
                .catch(err => reject(err));
        });
    });
}

/**
 * Remove generated .sage.py file (cross-platform)
 */
function removeSagePyFile(filePath: string): void {
    const sagePyFile = `${filePath}.py`;
    try {
        if (existsSync(sagePyFile)) {
            unlinkSync(sagePyFile);
        }
    } catch (err) {
        // Silently ignore if file doesn't exist or can't be deleted
        console.error(`Failed to remove ${sagePyFile}: ${err}`);
    }
}

/**
 * Build the command to run SageMath file based on platform
 */
function buildRunCommand(sagePath: string, filePath: string, dirPath: string): string {
    if (process.platform === 'win32') {
        // Windows: Use PowerShell compatible command
        return `cd "${dirPath}"; & "${sagePath}" "${filePath}"`;
    } else {
        // Unix-like: Use shell command
        return `cd '${dirPath}' && '${sagePath}' '${filePath}'`;
    }
}

// ============== Extension Activation ==============

export function activate(context: vscode.ExtensionContext) {
    // Command: Run SageMath File
    const runSageMathCommand = vscode.commands.registerCommand('sagemath-for-vscode.runSageMath', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found.');
            return;
        }

        const document = editor.document;
        await document.save();

        const sageMathPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('path');
        const condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');
        const condaEnvName = condaEnvPath ? basename(condaEnvPath) : undefined;

        if (!sageMathPath) {
            vscode.window.showErrorMessage('SageMath path is not configured. Please set it in settings.');
            return;
        }

        const filePath = editor.document.uri.fsPath;
        const dirPath = dirname(filePath);
        const command = buildRunCommand(sageMathPath, filePath, dirPath);
        const terminalName = !condaEnvPath ? 'SageMath' : `SageMath (${condaEnvName})`;

        let terminal = vscode.window.terminals.find((t: vscode.Terminal) => t.name === terminalName);

        if (!terminal) {
            terminal = vscode.window.createTerminal({
                name: terminalName,
            });
            if (condaEnvPath) {
                terminal.sendText(`conda activate "${condaEnvPath}"`);
            }
        }

        terminal.show(true);
        terminal.sendText(command);

        // Clean up .sage.py file after a delay (give SageMath time to finish)
        setTimeout(() => removeSagePyFile(filePath), 5000);
    });

    context.subscriptions.push(runSageMathCommand);


    // Command: Run Selected Code
    const runSelectedCodeCommand = vscode.commands.registerCommand('sagemath-for-vscode.runSelectedCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found.');
            return;
        }

        const selection = editor.selection;
        const selectedText = editor.document.getText(selection);

        if (!selectedText.trim()) {
            vscode.window.showWarningMessage('No code selected. Please select code to run.');
            return;
        }

        const sageMathPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('path');
        const condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');
        const condaEnvName = condaEnvPath ? basename(condaEnvPath) : undefined;

        if (!sageMathPath) {
            vscode.window.showErrorMessage('SageMath path is not configured. Please set it in settings.');
            return;
        }

        const terminalName = !condaEnvPath ? 'SageMath Interactive' : `SageMath Interactive (${condaEnvName})`;

        let terminal = vscode.window.terminals.find((t: vscode.Terminal) => t.name === terminalName);

        if (!terminal) {
            terminal = vscode.window.createTerminal({
                name: terminalName,
            });
            if (condaEnvPath) {
                terminal.sendText(`conda activate "${condaEnvPath}"`);
            }
            // Start SageMath interactive mode
            terminal.sendText(`"${sageMathPath}"`);
        }

        terminal.show(true);
        // Send selected code to the terminal
        terminal.sendText(selectedText);
    });

    context.subscriptions.push(runSelectedCodeCommand);


    // Command: Open SageMath Documentation
    const openDocumentationCommand = vscode.commands.registerCommand('sagemath-for-vscode.openDocumentation', async () => {
        const editor = vscode.window.activeTextEditor;
        let searchTerm = '';

        if (editor) {
            const selection = editor.selection;
            const selectedText = editor.document.getText(selection);
            if (selectedText.trim()) {
                searchTerm = selectedText.trim();
            } else {
                // Get word at cursor
                const wordRange = editor.document.getWordRangeAtPosition(selection.active);
                if (wordRange) {
                    searchTerm = editor.document.getText(wordRange);
                }
            }
        }

        let url = 'https://doc.sagemath.org/html/en/reference/';
        if (searchTerm) {
            url = `https://doc.sagemath.org/html/en/search.html?q=${encodeURIComponent(searchTerm)}`;
        }

        vscode.env.openExternal(vscode.Uri.parse(url));
    });

    context.subscriptions.push(openDocumentationCommand);


    // Command: Insert Docstring Template
    const insertDocstringCommand = vscode.commands.registerCommand('sagemath-for-vscode.insertDocstring', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found.');
            return;
        }

        const line = editor.document.lineAt(editor.selection.active.line);
        const lineText = line.text;

        // Check if current line is a function definition
        const funcMatch = lineText.match(/^(\s*)def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)/);
        if (funcMatch) {
            const indent = funcMatch[1] || '';
            const funcName = funcMatch[2];
            const params = funcMatch[3];

            // Parse parameters
            const paramList = params.split(',')
                .map(p => p.trim().split(':')[0].split('=')[0].trim())
                .filter(p => p && p !== 'self');

            // Build docstring
            let docstring = `${indent}    """Description of ${funcName}.\n\n`;

            if (paramList.length > 0) {
                docstring += `${indent}    Args:\n`;
                for (const param of paramList) {
                    docstring += `${indent}        ${param}: Description.\n`;
                }
                docstring += `\n`;
            }

            docstring += `${indent}    Returns:\n`;
            docstring += `${indent}        Description of return value.\n`;
            docstring += `${indent}    """\n`;

            // Insert docstring after the function definition
            const insertPosition = new vscode.Position(editor.selection.active.line + 1, 0);
            await editor.edit(editBuilder => {
                editBuilder.insert(insertPosition, docstring);
            });
        } else {
            vscode.window.showWarningMessage('Place cursor on a function definition line to insert docstring.');
        }
    });

    context.subscriptions.push(insertDocstringCommand);


    // Command: Show LSP Status
    const showLSPStatusCommand = vscode.commands.registerCommand('sagemath-for-vscode.showLSPStatus', async () => {
        if (isLSPStarted && client) {
            const state = client.state;
            const stateText = state === ClientState.Running ? 'Running' : 
                             state === ClientState.Starting ? 'Starting' : 
                             state === ClientState.Stopped ? 'Stopped' : 'Unknown';
            vscode.window.showInformationMessage(
                `SageMath LSP Status: ${stateText}\n` +
                `Version: 1.4.0\n` +
                `Features: Completion, Hover, Signatures, Diagnostics, Definition, References, Symbols, Folding, Rename, Code Actions`
            );
        } else {
            vscode.window.showWarningMessage('SageMath LSP is not running. Enable it in settings and restart VS Code.');
        }
    });

    context.subscriptions.push(showLSPStatusCommand);


    // Command: Setup Wizard
    const setupWizardCommand = vscode.commands.registerCommand('sagemath-for-vscode.setupWizard', async () => {
        await runSetupWizard(context);
    });
    context.subscriptions.push(setupWizardCommand);


    // Command: Check SageMath Status
    const checkStatusCommand = vscode.commands.registerCommand('sagemath-for-vscode.checkSageStatus', async () => {
        await checkSageStatus();
    });
    context.subscriptions.push(checkStatusCommand);


    // Command: Discover SageMath Installations
    const discoverCommand = vscode.commands.registerCommand('sagemath-for-vscode.discoverSage', async () => {
        const result = await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: '🔍 Searching for SageMath installations...',
            cancellable: false
        }, async () => {
            return await discoverSageInstallations();
        });

        if (result.installations.length === 0) {
            vscode.window.showWarningMessage('No SageMath installations found on your system.');
            return;
        }

        const items = result.installations.map(install => ({
            label: install === result.recommended ? `$(star) ${install.path}` : install.path,
            description: `${install.version || 'Unknown version'} (${install.type})`,
            detail: install === result.recommended ? 'Recommended' : undefined,
            installation: install
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a SageMath installation to use',
            title: `Found ${result.installations.length} SageMath Installation(s)`
        });

        if (selected) {
            const config = vscode.workspace.getConfiguration('sagemath-for-vscode.sage');
            await config.update('path', selected.installation.path, vscode.ConfigurationTarget.Global);
            
            if (selected.installation.type === 'conda') {
                const envPath = selected.installation.path.includes('Scripts')
                    ? selected.installation.path.replace(/[/\\]Scripts[/\\]sage(\.exe)?$/i, '')
                    : selected.installation.path.replace(/[/\\]bin[/\\]sage$/i, '');
                await config.update('condaEnvPath', envPath, vscode.ConfigurationTarget.Global);
            }
            
            vscode.window.showInformationMessage(
                `✅ SageMath configured: ${selected.installation.path} (${selected.installation.version || 'Unknown version'})`
            );
        }
    });
    context.subscriptions.push(discoverCommand);


    // Command: Show Installation Guide
    const installGuideCommand = vscode.commands.registerCommand('sagemath-for-vscode.showInstallGuide', async () => {
        const guide = getInstallationGuide();
        
        const items = guide.methods.map(method => ({
            label: method.recommended ? `$(star) ${method.name}` : method.name,
            description: method.description,
            detail: method.commands?.join(' | ') || method.url,
            method
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: `Select installation method for ${guide.platform}`,
            title: `🚀 SageMath Installation Guide - ${guide.platform}`
        });

        if (selected) {
            const method = selected.method;
            const panel = vscode.window.createWebviewPanel(
                'sagemathInstallGuide',
                `Install SageMath - ${method.name}`,
                vscode.ViewColumn.One,
                { enableScripts: true }
            );

            const commandsHtml = method.commands 
                ? method.commands.map(cmd => 
                    cmd.startsWith('#') 
                        ? `<p class="comment">${cmd}</p>` 
                        : cmd === '' 
                            ? '<br>' 
                            : `<code class="command">${cmd}</code>`
                ).join('\n')
                : '';

            const urlHtml = method.url 
                ? `<p><a href="${method.url}" class="link">📥 Download from official website</a></p>`
                : '';

            panel.webview.html = `<!DOCTYPE html>
<html>
<head>
    <style>
        body { 
            font-family: var(--vscode-font-family); 
            padding: 20px; 
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
        }
        h1 { color: var(--vscode-textLink-foreground); }
        .description { 
            margin: 16px 0; 
            padding: 12px;
            background: var(--vscode-textBlockQuote-background);
            border-left: 4px solid var(--vscode-textLink-foreground);
        }
        .command { 
            display: block;
            background: var(--vscode-terminal-background);
            color: var(--vscode-terminal-foreground);
            padding: 8px 12px;
            margin: 8px 0;
            border-radius: 4px;
            font-family: var(--vscode-editor-font-family);
            cursor: pointer;
        }
        .command:hover { background: var(--vscode-list-hoverBackground); }
        .comment { 
            color: var(--vscode-descriptionForeground);
            font-style: italic;
            margin: 16px 0 4px 0;
        }
        .link { 
            color: var(--vscode-textLink-foreground);
            text-decoration: none;
            padding: 8px 16px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border-radius: 4px;
            display: inline-block;
            margin: 16px 0;
        }
        .link:hover { background: var(--vscode-button-hoverBackground); }
        .tip {
            margin-top: 24px;
            padding: 12px;
            background: var(--vscode-inputValidation-infoBackground);
            border: 1px solid var(--vscode-inputValidation-infoBorder);
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>🚀 ${method.name}</h1>
    <div class="description">${method.description}</div>
    ${method.commands ? '<p>💡 Click on a command to copy it to clipboard</p>' : ''}
    ${commandsHtml}
    ${urlHtml}
    <div class="tip">
        <strong>💡 After installation:</strong><br>
        1. Close and reopen VS Code<br>
        2. Run command: <code>SageMath: Setup Wizard</code><br>
        3. The extension will auto-detect your new installation
    </div>
    <script>
        const vscode = acquireVsCodeApi();
        document.querySelectorAll('.command').forEach(el => {
            el.addEventListener('click', () => {
                navigator.clipboard.writeText(el.textContent);
                el.style.background = 'var(--vscode-inputValidation-infoBackground)';
                setTimeout(() => { el.style.background = ''; }, 500);
            });
        });
    </script>
</body>
</html>`;
        }
    });
    context.subscriptions.push(installGuideCommand);


    // Command: Select Conda Environment
    const selectCondaEnv = vscode.commands.registerCommand('sagemath-for-vscode.selectCondaEnv', async () => {
        try {
            const envs = await getCondaEnvs();
            if (envs.length === 0) {
                vscode.window.showInformationMessage('No Conda environments found.');
                return;
            }

            const selectedEnv = await vscode.window.showQuickPick(
                envs.map(env => ({ label: env.name, description: env.path })),
                { placeHolder: 'Select a Conda environment' }
            );

            if (selectedEnv) {
                const selectedPath = envs.find(env => env.name === selectedEnv.label)?.path;
                if (selectedPath) {
                    vscode.workspace.getConfiguration('sagemath-for-vscode.sage').update('condaEnvPath', selectedPath, true);
                    vscode.window.showInformationMessage(`Selected Conda environment: ${selectedEnv.label}`);
                }
            }
        } catch (error) {
            vscode.window.showErrorMessage(`${error}`);
        }
    });

    context.subscriptions.push(selectCondaEnv);


    // Function: start LSP
    function startLSP(envLSPpath: string): void {
        // LSP setup
        const pythonPath = process.platform === 'win32' ? join(envLSPpath, 'Scripts', 'python.exe') : join(envLSPpath, 'bin', 'python');
        const serverModule = context.asAbsolutePath(join('src', 'server', 'lsp.py'));
        const serverOptions: ServerOptions = {
            command: pythonPath,
            args: [serverModule],
            transport: TransportKind.stdio
        };
        const clientOptions: LanguageClientOptions = {
            documentSelector: [{ scheme: 'file', language: 'sagemath' }]
        };
        client = new LanguageClient(
            'sagemath-lsp',
            'SageMath Language Server',
            serverOptions,
            clientOptions
        );

        // LSP start with proper initialization handling
        client.start().then(() => {
            isLSPStarted = true;
            const logLevel = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP').get<string>('LSPLogLevel', 'info');
            client.sendNotification('sagemath/loglevel', { logLevel });
        }).catch((err: Error) => {
            vscode.window.showErrorMessage(`Failed to start SageMath LSP: ${err.message}`);
            isLSPStarted = false;
        });

        // Monitor LSP log level changes
        context.subscriptions.push(
            vscode.workspace.onDidChangeConfiguration((event: vscode.ConfigurationChangeEvent) => {
                if (event.affectsConfiguration('sagemath-for-vscode.LSP.LSPLogLevel')) {
                    const logLevel = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP').get<string>('LSPLogLevel', 'info');
                    client.sendNotification('sagemath/loglevel', { logLevel });
                    vscode.window.showInformationMessage(`SageMath Language Server log level updated to ${logLevel}.`);
                }
            })
        );
    }

    // If LSP enabled
    const useLSP = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP').get<boolean>('useSageMathLSP', true);
    if (!useLSP) {
        vscode.window.showInformationMessage('SageMath Language Server is disabled. Please enable it in settings and restart extension to use LSP features.');
    } else {
        // Start LSP
        const envLSPpath = context.asAbsolutePath(join('src', 'server', 'envLSP'));
        const requirementsPath = context.asAbsolutePath(join('src', 'server', 'requirements.txt'));

        (async () => {
            if (!existsSync(envLSPpath)) {
                const condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');

                if (!condaEnvPath) {
                    const action = await vscode.window.showWarningMessage(
                        'Conda environment is required for SageMath LSP. Please select a Conda environment first.',
                        'Select Environment',
                        'Disable LSP'
                    );

                    if (action === 'Select Environment') {
                        await vscode.commands.executeCommand('sagemath-for-vscode.selectCondaEnv');
                        // Re-check after selection
                        const newCondaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');
                        if (!newCondaEnvPath) {
                            vscode.window.showErrorMessage('No Conda environment selected. LSP will not be available.');
                            return;
                        }
                    } else {
                        return;
                    }
                }

                const currentCondaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');

                await vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: '📦 Creating Python venv for SageMath LSP...',
                    cancellable: false
                }, async () => {
                    try {
                        await createEnvLSP(envLSPpath, requirementsPath, currentCondaEnvPath);
                        vscode.window.showInformationMessage('✅ Python venv created successfully.');
                    } catch (err) {
                        vscode.window.showErrorMessage(`❌ Failed to create Python venv:\n${err}`);
                        if (existsSync(envLSPpath)) {
                            rmSync(envLSPpath, { recursive: true, force: true });
                        }
                    }
                });
            }

            if (existsSync(envLSPpath)) {
                try {
                    startLSP(envLSPpath);
                } catch (err) {
                    vscode.window.showErrorMessage(`❌ Failed to start SageMath LSP:\n${err}`);
                }
            }
        })();
    }

    // Command: LSP restart
    const restartLSP = vscode.commands.registerCommand('sagemath-for-vscode.restartLSP', async () => {
        if (client && client.state === ClientState.Running) {
            try {
                await client.stop();
                await client.start();
                isLSPStarted = true;
                vscode.window.showInformationMessage('SageMath Language Server restarted.');
            } catch (err) {
                isLSPStarted = false;
                vscode.window.showErrorMessage(`Failed to restart LSP: ${err}`);
            }
        } else {
            vscode.window.showWarningMessage('SageMath Language Server is not running.');
        }
    });

    context.subscriptions.push(restartLSP);


    // First-run detection: Check if SageMath is properly configured
    (async () => {
        const sagePath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('path', 'sage');
        const hasShownWizard = context.globalState.get<boolean>('hasShownSetupWizard', false);
        
        // Only auto-show wizard once per installation
        if (!hasShownWizard) {
            const validation = await validateSagePath(sagePath);
            
            if (!validation.valid) {
                const action = await vscode.window.showWarningMessage(
                    '⚠️ SageMath is not configured or not found on your system.',
                    'Run Setup Wizard',
                    'View Installation Guide',
                    'Dismiss'
                );

                if (action === 'Run Setup Wizard') {
                    await runSetupWizard(context);
                } else if (action === 'View Installation Guide') {
                    await vscode.commands.executeCommand('sagemath-for-vscode.showInstallGuide');
                }
                
                // Mark wizard as shown regardless of action
                await context.globalState.update('hasShownSetupWizard', true);
            } else {
                // SageMath is valid, mark as shown
                await context.globalState.update('hasShownSetupWizard', true);
            }
        }
    })();


    // Select Conda Environment button
    const condaEnvButton = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    condaEnvButton.text = '$(terminal) Select Conda Env';
    condaEnvButton.command = 'sagemath-for-vscode.selectCondaEnv';
    condaEnvButton.tooltip = 'SageMath for VScode: Select Conda Environment';

    // Monitor
    context.subscriptions.push(vscode.window.onDidChangeActiveTextEditor(editor => {
        if (editor && editor.document.languageId === 'sagemath') {
            condaEnvButton.show();
        } else {
            condaEnvButton.hide();
        }
    }));

    if (vscode.window.activeTextEditor &&
        vscode.window.activeTextEditor.document.languageId === 'sagemath') {
        condaEnvButton.show();
    }

    context.subscriptions.push(condaEnvButton);
}

// LSP shutdown
export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
