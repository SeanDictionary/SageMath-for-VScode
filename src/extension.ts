import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    // vscode.window.showInformationMessage('Activating SageMath for VSCode...');  // Test for activation

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
}