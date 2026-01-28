# Terminal Integration Architecture

## 1. Identity

- **What it is:** Terminal and Conda environment management for executing SageMath files and code.
- **Purpose:** Enables running `.sage` files or selected code in integrated terminals with automatic Conda environment activation and artifact cleanup.

## 2. Core Components

- `src/extension.ts` (runSageMathCommand): Command handler (F5) managing file save, terminal creation, and execution.
- `src/extension.ts` (runSelectedCodeCommand): Command handler (Shift+Enter) for interactive code execution.
- `src/extension.ts` (getCondaEnvs): Executes `conda env list --json` to discover available environments.
- `src/extension.ts` (selectCondaEnv): QuickPick interface for Conda environment selection.
- `src/extension.ts` (buildRunCommand): Platform-specific command generation for Windows PowerShell and Unix shells.
- `src/extension.ts` (removeSagePyFile): Cleanup handler for `.sage.py` intermediate files.

## 3. Execution Flow (LLM Retrieval Map)

**File Execution Flow (F5):**
- **Trigger:** User presses F5 or executes `sagemath-for-vscode.runSageMath` command.
- **Save Document:** Active editor is saved via `document.save()` (`src/extension.ts:142`).
- **Configuration Read:** Retrieves `sagemath-for-vscode.sage.path` and `sagemath-for-vscode.sage.condaEnvPath` from workspace config (`src/extension.ts:144-145`).
- **Terminal Lookup:** Searches for existing terminal named "SageMath" or "SageMath (env_name)".
- **Terminal Creation:** If not found, creates new terminal via `vscode.window.createTerminal()` (`src/extension.ts:161-163`).
- **Environment Activation:** If Conda path configured, sends `conda activate "<path>"` command (`src/extension.ts:165`).
- **Execution:** Builds platform-specific command and sends to terminal (`src/extension.ts:120-127`, `170`).
- **Cleanup:** Schedules `.sage.py` file deletion after 5-second delay (`src/extension.ts:173`).

**Selected Code Execution (Shift+Enter):**
- **Trigger:** User selects code and presses Shift+Enter or executes `runSelectedCode` command.
- **Validation:** Checks for active editor and non-empty selection (`src/extension.ts:181-193`).
- **Terminal Lookup:** Searches for "SageMath Interactive" or "SageMath Interactive (env_name)" terminal.
- **Terminal Creation:** If not found, creates terminal and starts SageMath interactive session via `sage` command (`src/extension.ts:208-216`).
- **Code Injection:** Sends selected code directly to interactive terminal (`src/extension.ts:221`).

**Conda Environment Discovery:**
- **Discovery Command:** Executes `conda env list --json` via Node.js `child_process.exec()` (`src/extension.ts:30`).
- **JSON Parsing:** Extracts environment names and paths from output, returns array of `{name, path}` objects (`src/extension.ts:35-49`).
- **User Selection:** Shows QuickPick UI via `vscode.window.showQuickPick()`.
- **Configuration Update:** Updates workspace setting `sagemath-for-vscode.sage.condaEnvPath` with selected path.

**Virtual Environment Creation (for LSP):**
- **Sage Python:** Uses `sage -python -m venv` instead of system Python (`src/extension.ts:89`).
- **Dependency Installation:** Executes `pip install -r requirements.txt` in newly created venv (`src/extension.ts:62`).
- **Platform Handling:** Constructs correct paths for Windows (`Scripts/pip.exe`) vs Unix (`bin/pip`) (`src/extension.ts:59-61`).
