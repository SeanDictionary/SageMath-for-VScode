# Extension Architecture Overview

## 1. Identity

- **What it is:** A VS Code extension providing language support for SageMath (.sage) files.
- **Purpose:** Enables editing, semantic highlighting, and execution of SageMath code within VS Code.

## 2. High-Level Description

The SageMath VS Code extension is a TypeScript-based extension that provides three core subsystems:

1. **Command Execution** - Runs SageMath files in integrated terminals with Conda environment support
2. **Language Server Protocol (LSP)** - Provides semantic highlighting through a Python-based language server
3. **Environment Management** - Discovers and manages Conda environments for SageMath execution

The extension follows a monolithic architecture with all client-side logic in `src/extension.ts`, which activates on command invocation and manages the LSP client lifecycle. The language server (`src/server/lsp.py`) runs as a separate Python process using pygls, communicating via stdio.

Key dependencies: `vscode-languageclient` for LSP client, `pygls` for LSP server. Configuration stored in workspace settings for SageMath path, Conda environment, and LSP behavior.
