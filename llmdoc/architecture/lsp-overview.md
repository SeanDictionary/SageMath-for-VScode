# SageMath LSP Architecture

## 1. Identity

- **What it is:** A lightweight Language Server Protocol (LSP) implementation for SageMath semantic highlighting.
- **Purpose:** Provides mathematical syntax highlighting for .sage files by recognizing SageMath-specific functions, classes, and operators.

## 2. High-Level Description

The LSP server is a Python process (`src/server/lsp.py`) launched by the VS Code extension via stdio transport. It implements a single-pass lexical and semantic analysis pipeline without building an AST, using regex-based tokenization and pattern matching for classification. The server maintains a comprehensive dictionary of SageMath standard library definitions (150+ functions, 30+ classes) and dynamically tracks user-defined symbols during analysis. Token data is delta-encoded and transmitted to the VS Code client for semantic highlighting.

**Core characteristics:** No AST construction, O(n) time complexity, single-file analysis scope, modular standard library definitions, configurable logging system.
