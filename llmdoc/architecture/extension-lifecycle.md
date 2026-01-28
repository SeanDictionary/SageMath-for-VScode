# Extension Lifecycle Architecture

## 1. Identity

- **What it is:** The activation, command registration, and LSP client initialization flow.
- **Purpose:** Defines how the extension starts up, registers user-facing commands, and establishes communication with the language server.

## 2. Core Components

- `package.json` (contributes, activationEvents): Extension manifest defining commands, keybindings, and entry point `./out/extension.js`.
- `src/extension.ts` (activate, deactivate): Main extension lifecycle handlers managing initialization and cleanup.
- `src/extension.ts` (startLSP): LanguageClient initialization with stdio transport to Python server.
- `src/extension.ts` (createEnvLSP, installRequirements): Virtual environment setup for LSP server dependencies.

## 3. Execution Flow (LLM Retrieval Map)

**Activation Phase:**
- **Entry Point:** VS Code loads `out/extension.js` compiled from `src/extension.ts` (no explicit activation events, commands trigger activation).
- **Command Registration:** `activate()` function (`src/extension.ts:125-347`) registers three commands:
  - `sagemath-for-vscode.runSageMath` - File execution handler
  - `sagemath-for-vscode.selectCondaEnv` - Conda environment selector
  - `sagemath-for-vscode.restartLSP` - LSP restart handler
- **LSP Initialization:** Checks `sagemath-for-vscode.LSP.useSageMathLSP` setting (`src/extension.ts:244`).
- **Environment Setup:** If `src/server/envLSP/` missing, prompts for Conda environment, creates venv via `sage -python -m venv` (`src/extension.ts:252-292`).
- **Server Start:** Calls `startLSP()` which creates LanguageClient with Python interpreter executing `src/server/lsp.py` (`src/extension.ts:202-241`).
- **Status Bar:** Creates Conda environment selection button visible for `.sage` files (`src/extension.ts:327-346`).

**Deactivation Phase:**
- **Cleanup:** `deactivate()` function (`src/extension.ts:350-355`) stops LanguageClient if running.

**Configuration Monitoring:**
- Watches `sagemath-for-vscode.LSP.LSPLogLevel` changes and sends custom `sagemath/loglevel` notification to server (`src/extension.ts:232-240`).

## 4. Design Rationale

- **Lazy LSP Activation:** LSP server starts after virtual environment setup to avoid failures from missing dependencies.
- **stdio Transport:** Uses standard input/output for client-server communication, avoiding network complexity.
- **Sage Python for Venv:** Uses `sage -python` instead of system Python to ensure compatibility with SageMath's Python environment.
- **Async Environment Creation:** Virtual environment setup runs asynchronously with progress indication to prevent blocking the UI.
- **No Workspace State:** Conda environment and LSP settings must be reconfigured per session (no persistence).
