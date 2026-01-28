# Syntax Highlighting System

## 1. Identity

- **What it is:** A dual-layer syntax highlighting system combining TextMate grammar with LSP-based semantic tokens for SageMath.
- **Purpose:** Provides accurate syntax highlighting and semantic classification for SageMath code in VS Code.

## 2. High-Level Description

The syntax highlighting system operates in two complementary layers:

1. **TextMate Grammar Layer** (`syntaxes/sagemath.tmLanguage.json`): Inherits Python's syntax highlighting and adds SageMath-specific comment patterns. Provides basic coloring for keywords, strings, operators, and comments.

2. **LSP Semantic Layer** (`src/server/lsp.py`, `src/server/utils.py`): Implements a custom Language Server that performs lexical and semantic analysis to classify functions, classes, methods, variables, and constants with SageMath-specific knowledge.

The TextMate grammar handles immediate visual feedback during typing, while the LSP server provides enhanced semantic understanding by recognizing SageMath's standard library (93 functions, 45 classes) and tracking user-defined symbols within the document.
