# SageMath LSP Architecture

## 1. Identity

- **What it is:** Full-featured Language Server Protocol (LSP) implementation for SageMath with 12+ protocol handlers.
- **Purpose:** Provides intelligent code assistance: semantic highlighting, completion, hover, signature help, navigation, diagnostics, code actions, and refactoring.

## 2. High-Level Description

The LSP server is a Python process (`src/server/lsp.py`) launched by the VS Code extension via stdio transport. It implements a modular architecture with specialized modules for documentation (`documentation.py`), symbol extraction (`symbols.py`), and code actions (`code_actions.py`). The server maintains a comprehensive database of SageMath documentation (50+ functions, 150+ methods with signatures, parameters, examples) and dynamically extracts user-defined symbols for document-aware features. Token data is delta-encoded and transmitted to VS Code for semantic highlighting.

**Core capabilities:** Semantic tokens, code completion (triggered by `.` and `(`), hover documentation with examples, signature help, go-to-definition, find-references, document symbols (outline), folding ranges, diagnostics (undefined variables, indentation, syntax), code actions (quick fixes, import insertion, docstring generation), rename symbols, inlay hints.

**Core characteristics:** No AST construction, O(n) analysis, single-file scope, modular documentation database, pygls framework, configurable logging.
