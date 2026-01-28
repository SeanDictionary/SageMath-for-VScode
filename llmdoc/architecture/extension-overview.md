# Extension Architecture Overview

## 1. Identity

- **What it is:** A VS Code extension providing language support for SageMath (.sage) files.
- **Purpose:** Enables editing, semantic highlighting, execution, and setup of SageMath within VS Code.

## 2. High-Level Description

The SageMath VS Code extension is a TypeScript-based extension that provides five core subsystems:

1. **Code Execution** - Runs SageMath files or selected code in integrated terminals with Conda environment support
2. **Language Server Protocol (LSP)** - Provides semantic highlighting through a Python-based language server
3. **Environment Management** - Discovers and manages Conda environments for SageMath execution
4. **Installation Discovery** - Auto-detects SageMath installations and provides setup wizards
5. **Documentation Integration** - Opens SageMath documentation and inserts docstring templates

The extension follows a monolithic architecture with client-side logic in `src/extension.ts` and `src/sageDiscovery.ts`. The language server (`src/server/lsp.py`) runs as a separate Python process using pygls, communicating via stdio.

Key dependencies: `vscode-languageclient` for LSP client, `pygls` for LSP server. Configuration stored in workspace settings for SageMath path, Conda environment, LSP behavior, code completion, diagnostics, run behavior, hover documentation, and inlay hints.
