# Terminal Integration Architecture

## 1. Identity

- **What it is:** Terminal and Conda environment management for executing SageMath files.
- **Purpose:** Enables running `.sage` files in integrated terminals with automatic Conda environment activation and artifact cleanup.

## 2. Core Components

- `src/extension.ts` (runSageMathCommand): Command handler (F5) managing file save, terminal creation, and execution.
- `src/extension.ts` (getCondaEnvs): Executes `conda env list --json` to discover available environments.
- `src/extension.ts` (selectCondaEnv): QuickPick interface for Conda environment selection.
- `src/extension.ts` (buildRunCommand): Platform-specific command generation for Windows PowerShell and Unix shells.
- `src/extension.ts` (removeSagePyFile): Cleanup handler for `.sage.py` intermediate files.

## 3. Execution Flow (LLM Retrieval Map)

**File Execution Flow:**
- **Trigger:** User presses F5 or executes `sagemath-for-vscode.runSageMath` command.
- **Save Document:** Active editor is saved via `document.save()` (`src/extension.ts:135`).
- **Configuration Read:** Retrieves `sagemath-for-vscode.sage.path` and `sagemath-for-vscode.sage.condaEnvPath` from workspace config (`src/extension.ts:137-138`).
- **Terminal Lookup:** Searches for existing terminal named "SageMath" or "SageMath (env_name)" (`src/extension.ts:151`).
- **Terminal Creation:** If not found, creates new terminal via `vscode.window.createTerminal()` (`src/extension.ts:154-156`).
- **Environment Activation:** If Conda path configured, sends `conda activate "<path>"` command to terminal (`src/extension.ts:157-159`).
- **Execution:** Builds platform-specific command (PowerShell on Windows, shell on Unix) and sends to terminal (`src/extension.ts:113-121`, `163`).
- **Cleanup:** Schedules `.sage.py` file deletion after 5-second delay via `removeSagePyFile()` (`src/extension.ts:166`).

**Conda Environment Discovery:**
- **Discovery Command:** Executes `conda env list --json` via Node.js `child_process.exec()` (`src/extension.ts:23`).
- **JSON Parsing:** Extracts environment names and paths from output, returns array of `{name, path}` objects (`src/extension.ts:28-37`).
- **User Selection:** Shows QuickPick UI via `vscode.window.showQuickPick()` (`src/extension.ts:181-184`).
- **Configuration Update:** Updates workspace setting `sagemath-for-vscode.sage.condaEnvPath` with selected path (`src/extension.ts:189`).

**Virtual Environment Creation (for LSP):**
- **Sage Python:** Uses `sage -python -m venv` instead of system Python to ensure SageMath compatibility (`src/extension.ts:82`).
- **Dependency Installation:** Executes `pip install -r requirements.txt` in newly created venv (`src/extension.ts:88`).
- **Platform Handling:** Constructs correct paths for Windows (`Scripts/python.exe`) vs Unix (`bin/python`) (`src/extension.ts:52-54`).

## 4. Design Rationale

- **Environment-Specific Terminals:** Each Conda environment gets dedicated terminal instance to avoid conflicts.
- **Fire-and-Forget Execution:** Terminal commands execute asynchronously without output capture (simpler but no error detection).
- **Delayed Cleanup:** 5-second delay on `.sage.py` deletion ensures SageMath finishes reading the intermediate file.
- **Cross-Platform Commands:** Separate command builders for PowerShell (Windows) and shell (Unix) handle syntax differences.
- **No Session Persistence:** Conda environment selection not persisted across sessions; must be reconfigured manually.
- **Status Bar Integration:** Conda environment button only visible when `.sage` file is active editor, reducing UI clutter.
