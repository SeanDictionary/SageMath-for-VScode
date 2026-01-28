# How to Extend Extension Commands

## 1. Add Command to package.json

Add command definition to the `contributes.commands` array in `package.json:63-118`:

```json
{
  "command": "sagemath-for-vscode.yourCommand",
  "title": "Your Command Title",
  "icon": "$(icon-name)"
}
```

Optional: Add keybinding in `contributes.keybindings` (`package.json:120-142`):

```json
{
  "command": "sagemath-for-vscode.yourCommand",
  "key": "ctrl+shift+y",
  "when": "editorLangId == sagemath"
}
```

## 2. Register Command Handler

In `src/extension.ts`, within the `activate()` function, register your command handler. Reference existing handlers in `src/extension.ts:134-510`:

```typescript
const yourCommand = vscode.commands.registerCommand(
  'sagemath-for-vscode.yourCommand',
  async () => {
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

Read workspace configuration using `vscode.workspace.getConfiguration()`. Configuration schema defined in `package.json:144-277`:

```typescript
const config = vscode.workspace.getConfiguration('sagemath-for-vscode.sage');
const sagePath = config.get<string>('path', 'sage');
```

Reference: `src/extension.ts:144-145`, `src/extension.ts:195-197`.

## 4. Show User Feedback

Use VS Code UI APIs for user interaction. Reference: `src/extension.ts:137`, `183-192`:

```typescript
// Error message
vscode.window.showErrorMessage('Operation failed');

// Warning message
vscode.window.showWarningMessage('No code selected');

// Info message
vscode.window.showInformationMessage('Operation succeeded');

// Quick pick selection
const selected = await vscode.window.showQuickPick(
  [{ label: 'Option 1' }, { label: 'Option 2' }],
  { placeHolder: 'Select an option' }
);
```

## 5. Organize Complex Commands

For commands requiring multiple functions or platform-specific logic, create a separate module. Reference: `src/sageDiscovery.ts`:

```typescript
// src/yourModule.ts
export async function yourComplexFunction(): Promise<void> {
  // Implementation
}

// src/extension.ts
import { yourComplexFunction } from './yourModule';
context.subscriptions.push(
  vscode.commands.registerCommand('sagemath-for-vscode.yourCommand', () => yourComplexFunction())
);
```

## 6. Verify

Press F5 to launch Extension Development Host, open a `.sage` file, and execute your command via keybinding or Command Palette.
