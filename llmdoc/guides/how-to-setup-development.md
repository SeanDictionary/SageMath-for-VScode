# How to Setup Development Environment

1. **Clone and Install**: Clone the repository and run `npm ci` to install dependencies.
2. **Open in VS Code**: Open the project folder in VS Code.
3. **Launch Development Host**: Press `F5` to launch the Extension Development Host. This automatically runs the watch build task (`.vscode/tasks.json`) and opens a new VS Code window with your extension loaded.
4. **Verify Loading**: The new window will show your extension as loaded. Check `.vscode/launch.json` for debug configuration.

**Tip**: The watch task (`tsc -watch -p ./`) runs in the background, automatically recompiling TypeScript on file changes.

## Verification Steps

1. Open a `.sage` file in the Extension Development Host.
2. Run the "SageMath for VScode: Run SageMath File" command from the Command Palette (`Ctrl+Shift+P`).
3. Check the VS Code Developer Tools Console for any errors.
4. Run `npm test` to execute integration tests (`src/test/runTest.ts`).

## Linting and Formatting

- **Lint code**: Run `npm run lint` to check ESLint compliance.
- **Fix linting**: Run `npm run lint:fix` to auto-fix ESLint issues.
- **Format code**: Run `npm run format` to apply Prettier formatting.
- **Check formatting**: Run `npm run format:check` to verify formatting without changes.
