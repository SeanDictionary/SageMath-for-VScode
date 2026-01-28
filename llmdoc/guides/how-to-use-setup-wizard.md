# How to Use Setup Wizard

## 1. Launch Setup Wizard

Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P) and execute "SageMath for VScode: Setup Wizard" or call `sagemath-for-vscode.setupWizard` command. Reference: `src/extension.ts:329-332`, `src/sageDiscovery.ts:195-285`.

## 2. Welcome Screen

Wizard displays welcome message with option to proceed. Select "Continue" to begin SageMath detection. Reference: `src/sageDiscovery.ts:195-220`.

## 3. Automatic Discovery

Wizard scans common SageMath installation paths on your system:
- **Windows:** Conda environments (miniconda3, anaconda3, mambaforge), Cygwin, WSL
- **macOS:** Homebrew, Conda, app bundles, system paths
- **Linux:** System packages, Conda environments, local installations

Reference: `src/sageDiscovery.ts:46-185`.

## 4. Select Installation

If SageMath found, wizard displays QuickPick with discovered installations. Each entry shows path, version, and type (system/conda/homebrew). Select preferred installation (marked with star if recommended). Reference: `src/extension.ts:357-383`.

## 5. Configuration

Wizard automatically updates VS Code settings:
- `sagemath-for-vscode.sage.path` - Set to selected SageMath executable
- `sagemath-for-vscode.sage.condaEnvPath` - Set if Conda installation selected

Reference: `src/extension.ts:370-378`.

## 6. No Installation Found

If no SageMath detected, wizard offers installation guide with platform-specific methods (Conda, Docker, source). Opens webview with copyable commands. Reference: `src/sageDiscovery.ts:329-380`, `src/extension.ts:389-499`.

## 7. Verify Configuration

Run "SageMath for VScode: Check SageMath Status" command to verify installation is correctly configured and view version information. Reference: `src/sageDiscovery.ts:287-324`.
