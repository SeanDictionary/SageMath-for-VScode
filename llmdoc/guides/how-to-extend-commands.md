# How to Extend Extension Commands

## 1. Add Command to package.json

Add command definition to the `contributes.commands` array in `package.json:57-72`:

```json
{
  "command": "sagemath-for-vscode.yourCommand",
  "title": "Your Command Title",
  "icon": "$(icon-name)"
}
```

Optional: Add keybinding in `contributes.keybindings` (`package.json:74-79`):

```json
{
  "command": "sagemath-for-vscode.yourCommand",
  "key": "ctrl+shift+y",
  "when": "editorLangId == sagemath"
}
```

## 2. Register Command Handler

In `src/extension.ts`, within the `activate()` function, register your command handler (`src/extension.ts:127-167` for reference):

```typescript
const yourCommand = vscode.commands.registerCommand(
  'sagemath-for-vscode.yourCommand',
  async () => {
    // Your implementation here
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage('No active editor');
      return;
    }
    // Command logic...
  }
);
context.subscriptions.push(yourCommand);
```

## 3. Access Configuration

Read workspace configuration using `vscode.workspace.getConfiguration()` (`src/extension.ts:137-138`):

```typescript
const config = vscode.workspace.getConfiguration('sagemath-for-vscode.sage');
const sagePath = config.get<string>('path', 'sage');
```

## 4. Show User Feedback

Use VS Code UI APIs for user interaction (`src/extension.ts:130`, `181-184`):

```typescript
// Error message
vscode.window.showErrorMessage('Operation failed');

// Info message
vscode.window.showInformationMessage('Operation succeeded');

// Quick pick selection
const selected = await vscode.window.showQuickPick(
  [{ label: 'Option 1' }, { label: 'Option 2' }],
  { placeHolder: 'Select an option' }
);
```

## 5. Verify

Press F5 to launch Extension Development Host, open a `.sage` file, and execute your command via keybinding or Command Palette.
