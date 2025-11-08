import * as vscode from 'vscode';
import path, { basename, join, dirname } from 'path';
import { existsSync, rmSync } from 'fs';
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
            const condaEnvName = condaEnvPath ? basename(condaEnvPath) : undefined;

            const filePath = editor.document.uri.fsPath;
            const dirpath = dirname(filePath);
            const command = `cd '${dirpath}' && sage '${filePath}'`;
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

            const fileFocus = true;

            terminal.show(fileFocus);
            terminal.sendText(command);
        });
    });

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
                    vscode.window.showInformationMessage(`Selected Conda environment: ${selectedEnv.label} with path ${selectedPath}`);
                }
            }
        } catch (error) {
            vscode.window.showErrorMessage(`${error}`);
        }
    });

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

    context.subscriptions.push(runSageMathCommand);
    context.subscriptions.push(selectCondaEnv);
    context.subscriptions.push(restartLSP);

    // Function: Check&Get Conda Env Path
    async function getCondaEnvPath() {
        let condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');
        if (!condaEnvPath) { vscode.window.showWarningMessage('Conda environment path for SageMath is not set. Please select a Conda environment.'); }
        while (!condaEnvPath) {
            await vscode.commands.executeCommand('sagemath-for-vscode.selectCondaEnv');
            await new Promise((r) => setTimeout(r, 1000));
            condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');
        }
        return condaEnvPath;
    }

    // TODO: Function: Auto-clone&install Sage LSP server

    // Function: Requirements check
    async function checkRequirements(): Promise<string[]> {
        const TARGET: string[] = [
            "sage-lsp-server"
        ]

        const missing: string[] = [];
        let checked = 0;

        const SageMathPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('path');
        const condaEnvPath = await getCondaEnvPath();
        const command = path.resolve(condaEnvPath!, SageMathPath!);

        return new Promise((resolve, reject) => {
            if (!SageMathPath) {
                vscode.window.showErrorMessage('SageMath path is not configured. \nPlease set sagemath-for-vscode.sage.path in settings.');
                resolve(TARGET);
                return;
            }

            TARGET.forEach((pkg) => {
                const cmd = `${command} -pip show ${pkg}`;
                try {
                    exec(cmd, (error, stdout, stderr) => {
                        checked++;
                        if (error || !stdout.includes(`Name: ${pkg}`)) {
                            missing.push(pkg);
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

    // Function: start LSP
    async function startLSP() {
        const SageMathPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('path');
        const condaEnvPath = await getCondaEnvPath();
        const command = path.resolve(condaEnvPath!, SageMathPath!);
        const serverOptions: ServerOptions = {
            run: {
                command: command,
                args: ['-python', '-m', 'pylsp'],
            },
            debug: {
                command: command,
                args: ['-python', '-m', 'pylsp', '-v'],
            },
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
    }


    const useLSP = vscode.workspace.getConfiguration('sagemath-for-vscode.LSP').get<boolean>('useSageMathLSP', true);
    if (!useLSP) {
        vscode.window.showInformationMessage('SageMath Language Server is disabled. Please enable it in settings and restart extnsion to use LSP features.');
    }
    else {
        // Start LSP
        (async () => {
            const missing = await checkRequirements();
            if (missing.length === 0) {
                await startLSP();
            } else {
                vscode.window.showErrorMessage(`Missing packages for LSP: ${missing.join(', ')}`);
            }
        })();
    }

    // Function: Get Conda Environments
    function getCondaEnvs(): Promise<{ name: string; path: string }[]> {
        return new Promise((resolve, reject) => {
            exec('conda env list --json', (error, stdout, stderr) => {
                if (error) {
                    reject(`Get Conda Eenvs Error: ${stderr}`);
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
                    reject(`Parse Conda Envs Error: ${parseError}`);
                    return;
                }
                resolve(envs);
            });
        });
    }

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
