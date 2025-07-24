import * as vscode from 'vscode';
import { basename, join, dirname } from 'path';
import { existsSync, unlinkSync } from 'fs';
import { exec } from 'child_process';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind,
    State as ClientState
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    // vscode.window.showInformationMessage('Activating SageMath for VSCode...');  // Test for activation

    // Command: Run SageMath File
    let runSageMathCommand = vscode.commands.registerCommand('sagemath-for-vscode.runSageMath', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found.');
            return;
        }

        const document = editor.document;
        document.save().then(() => {
            const SageMathPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('path');
            const condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');
            const condaEnvName = condaEnvPath ? basename(condaEnvPath) : undefined;

            if (!SageMathPath) {
                vscode.window.showErrorMessage('SageMath path is not configured. Please set it in settings.');
                return;
            }

            const filePath = editor.document.uri.fsPath;
            const dirpath = dirname(filePath);
            const command = `cd '${dirpath}' && ${SageMathPath} '${filePath}'`;
            const terminalName = !condaEnvPath ? 'SageMath' : `SageMath (${condaEnvName})`;

            let terminal = vscode.window.terminals.find(t => t.name === terminalName);

            if (!terminal) {
                terminal = vscode.window.createTerminal({
                    name: terminalName,
                });
                if (condaEnvPath) {
                    terminal.sendText(`conda activate ${condaEnvPath}`);
                }
            }

            terminal.show();
            terminal.sendText(command);
        });
    });

    context.subscriptions.push(runSageMathCommand);


    const useLSP = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP').get<boolean>('useSageMathLSP', true);
    if (!useLSP) {
        vscode.window.showInformationMessage('SageMath Language Server is disabled. Please enable it in settings and restart extnsion to use LSP features.');
    }
    else {
        // Function: install requirements
        function installRequirements(envLSPpath: string, requirementsPath: string): Promise<void> {
            return new Promise((resolve, reject) => {
                const pipPath = process.platform === 'win32' ? join(envLSPpath, 'Scripts', 'pip.exe') : join(envLSPpath, 'bin', 'pip');
                exec(`${pipPath} install -r ${requirementsPath}`, (error, stdout, stderr) => {
                    if (error) {
                        reject(`Install Requirements Error: ${stderr}`);
                        return;
                    }
                    resolve();
                });
            });
        }

        // Function: create venv for LSP
        function createEnvLSP(envLSPpath: string, requirementsPath: string): Promise<void> {
            return new Promise((resolve, reject) => {
                const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';
                exec(`${pythonCommand} -m venv ${envLSPpath}`, (error, stdout, stderr) => {
                    if (error) {
                        reject(`Create venv Error: ${stderr}`);
                        return;
                    }

                    installRequirements(envLSPpath, requirementsPath)
                        .then(() => resolve())
                        .catch(err => reject(err));
                });
            });
        }


        // Function: start LSP
        function startLSP(envLSPpath: string) {
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

            // LSP start
            client.start();
            const logLevel = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP').get<string>('LSPLogLevel', 'info');
            client.sendNotification('sagemath/loglevel', { logLevel });

            // Monitor LSP log level changes
            context.subscriptions.push(
                vscode.workspace.onDidChangeConfiguration((event) => {
                    if (event.affectsConfiguration('sagemath-for-vscode.LSP.LSPLogLevel')) {
                        const logLevel = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP').get<string>('LSPLogLevel', 'info');
                        client.sendNotification('sagemath/loglevel', { logLevel });
                        vscode.window.showInformationMessage(`SageMath Language Server log level updated to ${logLevel}.`);
                    }
                })
            );
        }

        // Start LSP
        const envLSPpath = context.asAbsolutePath(join('src', 'server', 'envLSP'));
        const requirementsPath = context.asAbsolutePath(join('src', 'server', 'requirements.txt'));
        (async () => {
            if (!existsSync(envLSPpath)) {
                await vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: '📦 Creating Python venv for SageMath LSP...',
                    cancellable: false
                }, async () => {
                    try {
                        await createEnvLSP(envLSPpath, requirementsPath);
                        vscode.window.showInformationMessage('✅ Python venv created.');
                        startLSP(envLSPpath);
                    } catch (err) {
                        vscode.window.showErrorMessage(`❌ Failed to creat Python venv: \n${err}`);
                        if (existsSync(envLSPpath)) { unlinkSync(envLSPpath); }
                    }
                });
            }
            else {
                startLSP(envLSPpath);
            }
        })();
    }

    // Command: LSP restart
    let restartLSP = vscode.commands.registerCommand('sagemath-for-vscode.restartLSP', async () => {
        if (client && client.state === ClientState.Running) {
            await client.stop();
            await client.start();
            vscode.window.showInformationMessage('SageMath Language Server restarted.');
        } else {
            vscode.window.showWarningMessage('SageMath Language Server not running.');
        }
    });

    context.subscriptions.push(restartLSP);


    // Function: Get Conda Environments
    function getCondaEnvs(): Promise<{ name: string; path: string }[]> {
        return new Promise((resolve, reject) => {
            exec('conda env list --json', (error, stdout, stderr) => {
                if (error) {
                    reject(`Get Conda Eenvs Error: ${stderr}`);
                    return;
                }

                const envs: { name: string; path: string }[] = [{ "name": "Global Environment", "path": "" }];

                try {
                    const data = JSON.parse(stdout);
                    if (data.envs) {
                        data.envs.forEach((envPath: string) => {
                            const envName = basename(envPath);
                            envs.push({ name: envName, path: envPath });
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

    // Command: Select Conda Environment
    let selectCondaEnv = vscode.commands.registerCommand('sagemath-for-vscode.selectCondaEnv', async () => {
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

    // // LSP restart button
    // const LSPrestartButton = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    // LSPrestartButton.text = '$(sync) Restart LSP';
    // LSPrestartButton.command = 'sagemath-for-vscode.restartLSP';
    // LSPrestartButton.tooltip = 'SageMath for VScode: Restart SageMath LSP';
    // context.subscriptions.push(LSPrestartButton);

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
