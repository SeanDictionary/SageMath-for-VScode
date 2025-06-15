import * as vscode from 'vscode';
import * as path from 'path';
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

    // runSageMathCommand command
    let runSageMathCommand = vscode.commands.registerCommand('sagemath-for-vscode.runSageMath', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found.');
            return;
        }

        const document = editor.document;
        document.save().then(() => {
            const SageMathPath = vscode.workspace.getConfiguration('sagemath-for-vscode').get<string>('path');
            if (!SageMathPath) {
                vscode.window.showErrorMessage('SageMath path is not configured. Please set it in settings.');
                return;
            }

            const filePath = editor.document.uri.fsPath;
            const command = `${SageMathPath} ${filePath}`;

            let terminal = vscode.window.terminals.find(t => t.name === 'SageMath');

            if (!terminal) {
                terminal = vscode.window.createTerminal({
                    name: 'SageMath',
                });
            }

            terminal.show();
            terminal.sendText(command);
        });
    });

    context.subscriptions.push(runSageMathCommand);

    // LSP setup
    const serverModule = context.asAbsolutePath(path.join('server', 'lsp.py'));
    const serverOptions: ServerOptions = {
        command: 'python',
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
    const logLevel = vscode.workspace.getConfiguration('sagemath-for-vscode').get<string>('LSPLogLevel', 'info');
    client.sendNotification('sagemath/loglevel', { logLevel });

    // LSP restart
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

    // Monitor LSP log level changes
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration((event) => {
            if (event.affectsConfiguration('sagemath-for-vscode.LSPLogLevel')) {
                const logLevel = vscode.workspace.getConfiguration('sagemath-for-vscode').get<string>('LSPLogLevel', 'info');
                client.sendNotification('sagemath/loglevel', { logLevel });
                vscode.window.showInformationMessage(`SageMath Language Server log level updated to ${logLevel}.`);
            }
        })
    );

    // // LSP restart button
    // const item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    // item.text = '$(sync) Restart LSP';
    // item.command = 'sagemath-for-vscode.restartLSP';
    // item.tooltip = 'SageMath for VScode: Restart SageMath LSP';
    // context.subscriptions.push(item);

    // // Monitor SageMath files
    // function monitorSageMath() {
    //     const editor = vscode.window.activeTextEditor;
    //     if (editor && editor.document.languageId === 'sagemath') {
    //         item.show();
    //     } else {
    //         item.hide();
    //     }
    // }

    // monitorSageMath();

    // context.subscriptions.push(
    //     vscode.window.onDidChangeActiveTextEditor(monitorSageMath)
    // );

    // context.subscriptions.push(
    //     vscode.workspace.onDidOpenTextDocument(monitorSageMath)
    // );
}

// LSP shutdown
export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
