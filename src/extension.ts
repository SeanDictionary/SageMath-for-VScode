import * as vscode from 'vscode';
import { dirname } from 'path';
import { exec } from 'child_process';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    State as ClientState
} from 'vscode-languageclient/node';

let client: LanguageClient;
const lspOutputChannel = vscode.window.createOutputChannel('SageMath Language Server');

const LANGUAGE_ID = 'sagemath';

let currentVersion = '0.0.0';

export function activate(context: vscode.ExtensionContext) {
    console.log('SageMath for VSCode is now active!');
    // vscode.window.showInformationMessage('Activating SageMath for VSCode...');  // Test for activation

    // Command: Run SageMath File
    let runSageMathCommand = vscode.commands.registerCommand('sagemath-for-vscode.runSageMath', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found.');
            return;
        }

        const document = editor.document;
        document.save().then(async () => {
            const condaEnvPath = await getCondaEnvPath();
            const envs = await getCondaEnvs();
            const condaEnvName = condaEnvPath ? (envs.find(env => env.path === condaEnvPath)?.name || 'Unknown Env') : 'Global';
            const PATH = condaEnvPath ? `${condaEnvPath}/bin:${process.env.PATH}` : process.env.PATH;
            const sagePath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('sagePath', 'sage');
            const filePath = editor.document.uri.fsPath;
            const workspacePath = vscode.workspace.workspaceFolders ? vscode.workspace.workspaceFolders[0].uri.fsPath : undefined;
            const dirPath = workspacePath ? workspacePath : dirname(filePath);
            const command = `cd '${dirPath}' && ${sagePath == 'sage' ? sagePath : `${condaEnvPath}/${sagePath}`} '${filePath}'; rm -f '${filePath}.py'`;
            const terminalName = `SageMath (${condaEnvName})`;

            let terminal = vscode.window.terminals.find(t => t.name === terminalName);

            if (!terminal) {
                terminal = vscode.window.createTerminal({
                    name: terminalName,
                    cwd: dirPath,
                    env: { ...process.env, PATH },
                });
                if (condaEnvPath) {
                    terminal.sendText(`conda activate ${condaEnvPath}`);
                }
            }

            const fileFocus = true;

            terminal.show(fileFocus);
            terminal.sendText(command);
        });
    });

    // Command: Select Conda Environment
    let selectCondaEnv = vscode.commands.registerCommand('sagemath-for-vscode.selectCondaEnv', async () => {
        try {
            const envs = await getCondaEnvs();
            const useGlobalEnv = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<boolean>('useGlobalEnv', false);
            const condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');
            const pickItems: (vscode.QuickPickItem & { envPath?: string; useGlobalEnv?: boolean })[] = [
                ...envs.map(env => ({ label: (!useGlobalEnv && condaEnvPath === env.path) ? `${env.name} (current)` : env.name, description: env.path, envPath: env.path })),
                { label: 'Options', kind: vscode.QuickPickItemKind.Separator },
                { label: useGlobalEnv ? 'Global Env (current)' : 'Global Env', description: 'Use the global SageMath environment', useGlobalEnv: true }
            ];

            const selectedEnv = await vscode.window.showQuickPick(
                pickItems,
                { placeHolder: 'Select a Conda environment' }
            );

            if (selectedEnv) {
                if (selectedEnv.useGlobalEnv) {
                    await vscode.workspace.getConfiguration('sagemath-for-vscode.sage').update('useGlobalEnv', true, true);
                    vscode.window.showInformationMessage('Using global SageMath environment.');
                    updateCondaEnvButton();
                } else {
                    const selectedPath = selectedEnv.envPath ?? envs.find(env => env.name === selectedEnv.label)?.path;
                    if (selectedPath) {
                        await vscode.workspace.getConfiguration('sagemath-for-vscode.sage').update('condaEnvPath', selectedPath, true);
                        await vscode.workspace.getConfiguration('sagemath-for-vscode.sage').update('useGlobalEnv', false, true);
                        vscode.window.showInformationMessage(`Selected Conda environment: \n\n${selectedEnv.label} with path ${selectedPath}`);
                        updateCondaEnvButton();
                    }
                }
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Error fetching Conda environments: ${error}`);
        }
    });

    // Command: LSP restart
    let restartLSPCommand = vscode.commands.registerCommand('sagemath-for-vscode.restartLSP', async () => {
        const useLSP = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP').get<boolean>('useSageMathLSP', true);
        if (!useLSP) {
            vscode.window.showWarningMessage('SageMath Language Server is disabled.');
            updateLSPStatusButton('disabled');
            return;
        }

        try {
            if (client && client.state !== ClientState.Stopped) {
                await client.stop();
            }

            const started = await startLSP();
            if (started) {
                vscode.window.showInformationMessage('SageMath Language Server restarted.');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to restart SageMath Language Server: ${error}`);
        }
    });

    // Command: Show LSP output
    let showLSPOutputCommand = vscode.commands.registerCommand('sagemath-for-vscode.showLSPOutput', () => {
        lspOutputChannel.show(true);
    });

    // Function: Check&Get Conda Env Path
    async function getCondaEnvPath() {
        const useGlobalEnv = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<boolean>('useGlobalEnv', false);
        if (useGlobalEnv) {
            return '';
        }
        let condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath', '');
        if (!condaEnvPath) {
            await vscode.commands.executeCommand('sagemath-for-vscode.selectCondaEnv');
            condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath', '');
        }
        return condaEnvPath;
    }

    // Function: Install Packages
    async function installPackage(pkg: string[], condaEnvPath: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const cmd = condaEnvPath ? `${condaEnvPath}/bin/pip install ${pkg.join(' ')}` : `pip install ${pkg.join(' ')}`;
            exec(cmd, (error, stdout, stderr) => {
                if (error) {
                    reject(`Failed to install packages: ${stderr}`);
                } else {
                    resolve();
                }
            });
        });
    }

    // Function: Requirements check
    async function checkRequirements(condaEnvPath: string): Promise<string[]> {
        const missing: string[] = [];
        let checked = 0;
        const TARGET: string[] = [
            "sage-lsp"
        ]

        return new Promise((resolve, reject) => {
            TARGET.forEach((pkg) => {
                const cmd = condaEnvPath ? `${condaEnvPath}/bin/pip show ${pkg}` : `pip show ${pkg}`;
                try {
                    exec(cmd, (error, stdout, stderr) => {
                        checked++;
                        if (error || !stdout.includes(`Name: ${pkg}`)) {
                            missing.push(pkg);
                        } else {
                            const versionMatch = stdout.match(/Version:\s*(.*)/);
                            if (versionMatch) {
                                currentVersion = versionMatch[1].trim();
                            }
                        }

                        if (checked === TARGET.length) {
                            resolve(missing);
                        }
                    });
                } catch (err) {
                    reject(`Requirement Check Error: ${err}`);
                }
            });

            if (TARGET.length === 0) {
                resolve([]);
            }
        });
    }

    // Function: Check Requirements version
    async function checkRequirementsVersion(condaEnvPath: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const url = 'https://api.github.com/repos/SeanDictionary/sage-lsp/releases/latest';
            const cmd = `curl -s ${url}`;
            exec(cmd, async (error, stdout, stderr) => {
                if (error) {
                    reject(`Failed to fetch latest release: ${stderr}`);
                    return;
                }
                
                try {
                    const data = JSON.parse(stdout);
                    const latestVersion = String(data.tag_name || '').replace(/^v/, '');
                    console.log(`Current LSP version: ${currentVersion}, Latest LSP version: ${latestVersion}`);
                    if (currentVersion !== latestVersion) {
                        const updateChoice = await vscode.window.showInformationMessage(
                            `A new version of sage-lsp is available: ${latestVersion} (current: ${currentVersion}).`,
                            'Update',
                            'Later'
                        );

                        if (updateChoice === 'Update') {
                            await vscode.window.withProgress(
                                {
                                    location: vscode.ProgressLocation.Notification,
                                    title: 'Updating sage-lsp',
                                    cancellable: false
                                },
                                async () => {
                                    await installPackage(['--upgrade', 'sage-lsp'], condaEnvPath);
                                }
                            );
                            vscode.window.showInformationMessage(`sage-lsp has been updated to ${latestVersion}.`);
                            await vscode.commands.executeCommand('sagemath-for-vscode.restartLSP');
                        }
                    }
                    resolve();
                } catch (err) {
                    reject(`Failed to parse latest release: ${err}`);
                }
            });
        });
    }

    // Function: Stop LSP
    async function stopLSP() {
        if (client && client.state !== ClientState.Stopped) {
            await client.stop();
            updateLSPStatusButton('stopped');
        }
    }

    // Function: start LSP
    async function startLSP(): Promise<boolean> {
        // Abort if LSP is already running
        await stopLSP();

        const useLSP = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP').get<boolean>('useSageMathLSP', true);
        if (!useLSP) {
            vscode.window.showInformationMessage('SageMath Language Server is disabled.');
            updateLSPStatusButton('disabled');
            return false;
        }

        const condaEnvPath = await getCondaEnvPath();
        const missing = await checkRequirements(condaEnvPath);
        if (missing.length !== 0) {
            const installChoice = await vscode.window.showErrorMessage(
                `Missing packages for LSP: ${missing.join(', ')} \nCurrent environment: ${condaEnvPath || 'Global'}`,
                'Install',
                'Cancel'
            );
            updateLSPStatusButton('error', `Missing packages: ${missing.join(', ')}`);

            if (installChoice !== 'Install') {
                return false;
            } else {
                try {
                    updateLSPStatusButton('starting');
                    await vscode.window.withProgress(
                        {
                            location: vscode.ProgressLocation.Notification,
                            title: 'Installing SageMath LSP dependencies',
                            cancellable: false
                        },
                        async (progress) => {
                            progress.report({
                                message: `Current environment: ${condaEnvPath || 'Global'}`
                            });
                            await installPackage(missing, condaEnvPath);
                        }
                    );
                    vscode.window.showInformationMessage(`Installed packages for LSP: ${missing.join(', ')}`);
                } catch (error) {
                    const detail = String(error);
                    vscode.window.showErrorMessage(`Failed to install packages: ${detail}`);
                    updateLSPStatusButton('error', detail);
                    return false;
                }
            }
        }

        checkRequirementsVersion(condaEnvPath).catch(error => {
            console.error(`Version check failed: ${error}`);
        });

        const command = condaEnvPath ? `${condaEnvPath}/bin/python` : 'python';
        const PATH = condaEnvPath ?`${condaEnvPath}/bin:${process.env.PATH}` : process.env.PATH;
        const LogLevel = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP').get<string>('LSPLogLevel', 'INFO');
        const serverOptions: ServerOptions = {
            run: {
                command: command,
                args: ["-m", "sagelsp", "--log", LogLevel],
                options: { env: { ...process.env, PATH } },
            },
            debug: {
                command: command,
                args: ["-m", "sagelsp", "--log", "DEBUG"],
                options: { env: { ...process.env, PATH } },
            },
        };
        const clientOptions: LanguageClientOptions = {
            documentSelector: [
                { scheme: 'file', language: LANGUAGE_ID },
                { notebook: 'jupyter-notebook', language: LANGUAGE_ID },
            ],
            outputChannel: lspOutputChannel,
        };
        client = new LanguageClient(
            'sagemath-lsp',
            'SageMath Language Server',
            serverOptions,
            clientOptions
        );

        client.onDidChangeState((e) => {
            switch (e.newState) {
                case ClientState.Starting:
                    updateLSPStatusButton('starting');
                    break;
                case ClientState.Running:
                    updateLSPStatusButton('running');
                    break;
                case ClientState.Stopped:
                    updateLSPStatusButton('stopped');
                    break;
            }
        });

        try {
            await client.start();
            return true;
        } catch (error) {
            updateLSPStatusButton('error', String(error));
            throw error;
        }
    }

    // Function: Get Conda Environments
    async function getCondaEnvs(): Promise<{ name: string; path: string }[]> {
        return new Promise((resolve, reject) => {
            const condaPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaPath', 'conda');
            const cmd = `
            ${condaPath} env list --json
            `;
            exec(cmd, (error, stdout, stderr) => {
                if (error) {
                    reject(`Get Conda Envs Error: ${stderr}`);
                    return;
                }

                const envs: { name: string; path: string }[] = [];

                try {
                    const data = JSON.parse(stdout);
                    if (data.envs) {
                        data.envs.forEach((envPath: string) => {
                            const env = data.envs_details[envPath];
                            envs.push({ name: env.name, path: envPath });
                        });
                    }
                } catch (parseError) {
                    reject(`Parse Conda Envs Error: ${parseError}`);
                    return;
                }
                resolve(envs);
            });
        });
    }

    // Function: Update Conda Env Button Text
    async function updateCondaEnvButton() {
        const useGlobalEnv = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<boolean>('useGlobalEnv', false);
        if (useGlobalEnv) {
            condaEnvButton.text = '$(terminal) Global';
            condaEnvButton.tooltip = 'SageMath for VScode: Using Global SageMath Environment';
            return;
        }
        const condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');
        if (condaEnvPath) {
            const envs = await getCondaEnvs();
            const condaEnvName = condaEnvPath ? (envs.find(env => env.path === condaEnvPath)?.name || 'Unknown Env') : 'Global';
            condaEnvButton.text = `$(terminal) ${condaEnvName}`;
            condaEnvButton.tooltip = `SageMath for VScode: Current Environment\n${condaEnvPath}`;
        } else {
            condaEnvButton.text = '$(terminal) Select Conda Env';
            condaEnvButton.tooltip = 'SageMath for VScode: Select Conda Environment';
        }
    }

    // Function: Update LSP Status Button
    function updateLSPStatusButton(status: 'starting' | 'running' | 'stopped' | 'disabled' | 'error', detail?: string) {
        switch (status) {
            case 'starting':
                lspStatusButton.text = '$(loading~spin) LSP';
                lspStatusButton.tooltip = 'SageMath Language Server is starting...';
                break;
            case 'running':
                lspStatusButton.text = '$(check) LSP';
                lspStatusButton.tooltip = 'SageMath Language Server is running.';
                break;
            case 'stopped':
                lspStatusButton.text = '$(circle-slash) LSP';
                lspStatusButton.tooltip = 'SageMath Language Server is stopped.';
                break;
            case 'disabled':
                lspStatusButton.text = '$(debug-disconnect) LSP';
                lspStatusButton.tooltip = 'SageMath Language Server is disabled.';
                break;
            case 'error':
                lspStatusButton.text = '$(error) LSP';
                lspStatusButton.tooltip = detail ? `SageMath Language Server error:\n${detail}` : 'SageMath Language Server failed.';
                break;
        }
    }

    // Monitor configuration changes
    let configChangeMonitor = vscode.workspace.onDidChangeConfiguration(async (e) => {
        if (e.affectsConfiguration('sagemath-for-vscode.sage.condaEnvPath') || e.affectsConfiguration('sagemath-for-vscode.sage.useGlobalEnv')) {
            await updateCondaEnvButton();
            if (vscode.workspace.getConfiguration('sagemath-for-vscode.LSP').get<boolean>('useSageMathLSP', true)) {
                await vscode.commands.executeCommand('sagemath-for-vscode.restartLSP');
            }
        }
        if (e.affectsConfiguration('sagemath-for-vscode.LSP.useSageMathLSP')) {
            const useLSP = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP').get<boolean>('useSageMathLSP', true);
            if (useLSP && (!client || client.state === ClientState.Stopped)) {
                await startLSP();
            } else if (!useLSP && client && client.state !== ClientState.Stopped) {
                await stopLSP();
            }

            if (!useLSP) {
                updateLSPStatusButton('disabled');
            }
        }
        if (e.affectsConfiguration('sagemath-for-vscode.LSP.LSPLogLevel')) {
            await vscode.commands.executeCommand('sagemath-for-vscode.restartLSP');
        }
    })

    // Monitor active editor changes
    let editorChangeMonitor = vscode.window.onDidChangeActiveTextEditor(async (e) => {
        if (e && e.document.languageId === LANGUAGE_ID) {
            condaEnvButton.show();
            lspStatusButton.show();
        } else {
            condaEnvButton.hide();
            lspStatusButton.hide();
        }
    });

    // Select Conda Environment button
    const condaEnvButton = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    condaEnvButton.command = 'sagemath-for-vscode.selectCondaEnv';
    condaEnvButton.tooltip = 'SageMath for VScode: Select Conda Environment';

    // LSP Status button
    const lspStatusButton = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 99);
    lspStatusButton.command = 'sagemath-for-vscode.showLSPOutput';
    lspStatusButton.tooltip = 'SageMath Language Server Status';

    context.subscriptions.push(runSageMathCommand);
    context.subscriptions.push(selectCondaEnv);
    context.subscriptions.push(restartLSPCommand);
    context.subscriptions.push(showLSPOutputCommand);
    context.subscriptions.push(condaEnvButton);
    context.subscriptions.push(lspStatusButton);
    context.subscriptions.push(configChangeMonitor);
    context.subscriptions.push(editorChangeMonitor);

    if (vscode.window.activeTextEditor && vscode.window.activeTextEditor.document.languageId === LANGUAGE_ID) {
        condaEnvButton.show();
        lspStatusButton.show();
    }

    // Initial setup
    async function initialize() {
        try {
            // Initialize button text
            await updateCondaEnvButton();

            // Start LSP
            await startLSP();
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to start SageMath Language Server: ${error}`);
        }
    };

    initialize();
}

// LSP shutdown
export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
