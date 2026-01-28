# LSP Capabilities Architecture

## 1. Identity

- **What it is:** Full-featured Language Server implementation with 12+ LSP protocol handlers.
- **Purpose:** Provides intelligent code assistance including completion, hover, signature help, navigation, diagnostics, and refactoring.

## 2. Core Components

- `src/server/lsp.py:1-919` (LSP handlers): Complete LSP protocol implementation with pygls decorators.
- `src/server/documentation.py:1-634` (FUNCTION_DOCS, METHOD_DOCS): Comprehensive SageMath function/method documentation database.
- `src/server/symbols.py:33-487` (SymbolExtractor): Symbol extraction for outline, navigation, and completion.
- `src/server/code_actions.py:20-473` (CodeActionProvider): Quick fixes, refactoring, and source actions.
- `src/server/predefinition.py:1-193` (FUNCTIONS, CLASSES): Standard library definitions for semantic recognition.

## 3. Execution Flow (LLM Retrieval Map)

### Completion Flow
- **Trigger**: `.` or `(` typed → `lsp.py:328-433` (completions)
- **Context**: `get_context_at_position()` determines dot vs. global → `lsp.py:79-106`
- **User symbols**: `get_user_completions()` extracts document symbols → `lsp.py:873-913`
- **Documentation**: `get_function_doc()` retrieves from `documentation.py:564-566`
- **Return**: `CompletionList(is_incomplete, items)`

### Hover Flow
- **Trigger**: Cursor hover → `lsp.py:437-503` (hover)
- **Word extraction**: `get_word_at_position()` → `lsp.py:59-76`
- **Documentation lookup**: `get_function_doc()` or `get_method_doc()` → `documentation.py:564-573`
- **Format**: `format_hover_markdown()` generates Markdown → `documentation.py:588-617`

### Diagnostics Flow
- **Trigger**: Document open/change/save → `lsp.py:561-584` (did_open, did_change, did_save)
- **Analysis**: `check_diagnostics()` scans for undefined variables, indentation issues, syntax errors → `lsp.py:193-284`
- **Publish**: `ls.publish_diagnostics()` sends to VS Code

### Navigation Flow
- **Definition**: `definition()` → `find_definitions_in_doc()` → `lsp.py:589-611, 145-172`
- **References**: `references()` → `find_references_in_doc()` → `lsp.py:615-629, 175-190`

### Code Actions Flow
- **Trigger**: Quick Fix requested → `lsp.py:733-754` (code_action)
- **Delegation**: `CodeActionProvider.get_code_actions()` → `code_actions.py:118-145`
- **Action types**: Import insertion, typo correction, indentation fix, docstring generation → `code_actions.py:147-473`

## 4. Design Rationale

Modular separation of concerns: documentation in `documentation.py`, symbol extraction in `symbols.py`, code actions in `code_actions.py`, protocol handling in `lsp.py`. Single-pass analysis maintains O(n) performance. User-defined symbols extracted once per document and cached (`symbol_extractor_cache`). Documentation database structured for efficient lookup by function/class name. Code actions use Levenshtein distance for typo suggestions (threshold: ≤2 edits).
