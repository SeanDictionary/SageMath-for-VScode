# Extension Lifecycle Architecture

## 1. Identity

- **What it is:** The activation, command registration, and LSP client initialization flow.
- **Purpose:** Defines how the extension starts up, registers user-facing commands, and establishes communication with the language server.

## 2. Core Components

- `package.json` (contributes, activationEvents): Extension manifest defining 11 commands, keybindings, and entry point `./out/extension.js`.
- `src/extension.ts` (activate, deactivate): Main extension lifecycle handlers managing initialization and cleanup.
- `src/extension.ts` (startLSP): LanguageClient initialization with stdio transport to Python server.
- `src/extension.ts` (createEnvLSP, installRequirements): Virtual environment setup for LSP server dependencies.
- `src/sageDiscovery.ts` (runSetupWizard, checkSageStatus, discoverSageInstallations): SageMath installation detection and setup.

## 3. Execution Flow (LLM Retrieval Map)

**Activation Phase:**
- **Entry Point:** VS Code loads `out/extension.js` compiled from `src/extension.ts` (no explicit activation events, commands trigger activation).
- **Command Registration:** `activate()` function (`src/extension.ts:132-510`) registers 11 commands:
  - `runSageMath` - Execute entire .sage file (F5)
  - `runSelectedCode` - Execute selected code in interactive mode (Shift+Enter)
  - `openDocumentation` - Open SageMath docs (Ctrl+Shift+D)
  - `insertDocstring` - Insert docstring template (Ctrl+Shift+/)
  - `showLSPStatus` - Display LSP server state
  - `setupWizard` - First-time setup wizard
  - `checkSageStatus` - Validate SageMath installation
  - `discoverSage` - Auto-detect SageMath installations
  - `showInstallGuide` - Display installation instructions
  - `selectCondaEnv` - Conda environment selector
  - `restartLSP` - LSP restart handler
- **LSP Initialization:** Checks `sagemath-for-vscode.LSP.useSageMathLSP` setting.
- **Environment Setup:** If `src/server/envLSP/` missing, creates venv via `sage -python -m venv` and installs dependencies.
- **Server Start:** Calls `startLSP()` which creates LanguageClient with Python interpreter executing `src/server/lsp.py`.
- **Status Bar:** Creates Conda environment selection button visible for `.sage` files.

**Deactivation Phase:**
- **Cleanup:** `deactivate()` function stops LanguageClient if running.

**Configuration Monitoring:**
- Watches `sagemath-for-vscode.LSP.LSPLogLevel` changes and sends custom `sagemath/loglevel` notification to server.

## 4. Design Rationale

- **Lazy LSP Activation:** LSP server starts after virtual environment setup to avoid failures from missing dependencies.
- **stdio Transport:** Uses standard input/output for client-server communication, avoiding network complexity.
- **Sage Python for Venv:** Uses `sage -python` instead of system Python to ensure compatibility with SageMath's Python environment.
- **Async Environment Creation:** Virtual environment setup runs asynchronously with progress indication to prevent blocking the UI.
- **No Workspace State:** Conda environment and LSP settings must be reconfigured per session (no persistence).
