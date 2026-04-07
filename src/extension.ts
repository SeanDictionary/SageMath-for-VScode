import * as vscode from 'vscode';
import path, { basename, dirname } from 'path';
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
            const command = `cd '${dirpath}' && sage '${filePath}'; rm -f '${filePath}.py'`;
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
            const pickItems: (vscode.QuickPickItem & { envPath?: string; useGlobalEnv?: boolean })[] = [
                ...envs.map(env => ({ label: env.name, description: env.path, envPath: env.path })),
                { label: 'Options', kind: vscode.QuickPickItemKind.Separator },
                { label: 'Using Global Env', description: 'Use the global SageMath environment', useGlobalEnv: true }
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
    // TODO: bug fix
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
        let useGlobalEnv = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<boolean>('useGlobalEnv', false);
        if (useGlobalEnv) {
            return '';
        }
        let condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');
        if (!condaEnvPath) {
            await vscode.commands.executeCommand('sagemath-for-vscode.selectCondaEnv');
            await new Promise((r) => setTimeout(r, 1000));
            condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');
        }
        return condaEnvPath;
    }

    // TODO: Function: Auto-clone&install Sage LSP server
    //      Clone from https://github.com/SeanDictionary/sage-lsp and using `pip install ./sage-lsp` to install

    // Function: Requirements check
    async function checkRequirements(): Promise<string[]> {
        const TARGET: string[] = [
            "sage-lsp"
        ]

        const missing: string[] = [];
        let checked = 0;

        const condaEnvPath = await getCondaEnvPath();

        return new Promise((resolve, reject) => {
            TARGET.forEach((pkg) => {
                const cmd = `${condaEnvPath}/bin/pip show ${pkg}`;
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
        const lspPath = './bin/sagelsp';
        const condaEnvPath = await getCondaEnvPath();
        const command = path.resolve(condaEnvPath!, './bin/python');
        const PATH = `${condaEnvPath}/bin:${process.env.PATH}`;
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
        vscode.window.showInformationMessage('SageMath Language Server is disabled.');
    }
    else {
        // Start LSP
        (async () => {
            const missing = await checkRequirements();
            if (missing.length === 0) {
                await startLSP();
            } else {
                vscode.window.showErrorMessage(`Missing packages for LSP: ${missing.join(', ')}\n`);
            }
        })();
    }

    // Function: Get Conda Environments
    function getCondaEnvs(): Promise<{ name: string; path: string }[]> {
        return new Promise((resolve, reject) => {
            const condaPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaPath', 'conda');
            const cmd = `
            ${condaPath} env list --json
            `;
            exec(cmd, { shell: "/bin/bash" }, (error, stdout, stderr) => {
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
    condaEnvButton.command = 'sagemath-for-vscode.selectCondaEnv';
    condaEnvButton.tooltip = 'SageMath for VScode: Select Conda Environment';

    // Function: Update Conda Env Button Text
    function updateCondaEnvButton() {
        const useGlobalEnv = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<boolean>('useGlobalEnv', false);
        if (useGlobalEnv) {
            condaEnvButton.text = '$(terminal) Global';
            condaEnvButton.tooltip = 'SageMath for VScode: Using Global SageMath Environment';
            return;
        }
        const condaEnvPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('condaEnvPath');
        if (condaEnvPath) {
            const envName = basename(condaEnvPath);
            condaEnvButton.text = `$(terminal) ${envName}`;
            condaEnvButton.tooltip = `SageMath for VScode: Current Environment - ${envName}\nPath: ${condaEnvPath}`;
        } else {
            condaEnvButton.text = '$(terminal) Select Conda Env';
            condaEnvButton.tooltip = 'SageMath for VScode: Select Conda Environment';
        }
    }

    // Initialize button text
    updateCondaEnvButton();

    // Monitor configuration changes
    context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(e => {
        if (e.affectsConfiguration('sagemath-for-vscode.sage.condaEnvPath') || e.affectsConfiguration('sagemath-for-vscode.sage.useGlobalEnv')) {
            updateCondaEnvButton();
        }
    }));

    // Monitor active editor changes
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
