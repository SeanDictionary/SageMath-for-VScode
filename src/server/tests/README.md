# SageMath LSP Server Tests

This directory contains comprehensive unit tests for the SageMath Language Server Protocol (LSP) implementation.

## Test Coverage Summary

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_lsp.py` | 55+ | LSP helper functions: word/context extraction, definitions, references, diagnostics, user completions |
| `test_lsp_protocol.py` | 60+ | LSP protocol compliance: initialize, completion, hover, signature, definition, references, diagnostics, semantic tokens |
| `test_utils.py` | 60+ | Utility classes: Logging, Token, SemanicSever (parsing, classification) |
| `test_documentation.py` | 50+ | Documentation functions: format_hover, get_function_doc, data completeness |
| `test_predefinition.py` | 30+ | Predefined data: TOKEN_TYPES, KEYWORDS, FUNCTIONS, CLASSES |
| `test_symbols.py` | 50+ | Symbol extraction: functions, classes, variables, type inference, SageMath patterns |
| `test_code_actions.py` | 45+ | Code actions: quick fixes, import suggestions, typo corrections, docstring generation |

**Total: 350+ tests**

## Test Structure

```text
tests/
├── __init__.py            # Package marker
├── conftest.py            # Pytest fixtures and configuration
├── test_lsp.py            # LSP helper functions tests
├── test_lsp_protocol.py   # LSP protocol compliance tests
├── test_utils.py          # Utility classes tests
├── test_documentation.py  # Documentation functions tests
├── test_predefinition.py  # Predefined constants tests
├── test_symbols.py        # Symbol extraction tests (v1.4.0)
└── test_code_actions.py   # Code actions tests (v1.4.0)
```

## Running Tests

### Prerequisites

This project uses [uv](https://github.com/astral-sh/uv) for Python environment management.

Install uv (if not already installed):

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Setup the development environment:

```bash
cd src/server
uv sync --dev
```

### Run All Python Tests

From the project root:

```bash
npm run test:python
```

Or directly with uv:

```bash
cd src/server
uv run pytest tests/ -v
```

### Run Specific Test File

```bash
uv run pytest tests/test_lsp.py -v
```

### Run Specific Test Class

```bash
uv run pytest tests/test_lsp.py::TestGetWordAtPosition -v
```

### Run with Coverage

```bash
npm run test:python:cov
```

Or:

```bash
uv run pytest tests/ -v --cov=. --cov-report=html
```

Coverage report will be generated in `htmlcov/` directory.

## Test Categories

### test_lsp.py

- `TestGetWordAtPosition` - Word extraction at cursor position
- `TestGetContextAtPosition` - Context detection for completions
- `TestGetFunctionAtPosition` - Function call detection for signature help
- `TestFindDefinitionsInDoc` - Go to definition functionality
- `TestFindReferencesInDoc` - Find all references functionality
- `TestCheckDiagnostics` - Code diagnostics and warnings

### test_utils.py

- `TestLogging` - Logging class with level filtering
- `TestToken` - Semantic token representation
- `TestRegexPatterns` - Tokenization regex patterns
- `TestSemanicSeverDocToTokens` - Document tokenization
- `TestSemanicSeverClassifyTokens` - Token classification
- `TestSemanicSeverParse` - Full parsing pipeline

### test_documentation.py

- `TestFunctionDocs` - Function documentation data structure
- `TestMethodDocs` - Method documentation data structure
- `TestGetFunctionDoc` - Function doc retrieval
- `TestGetMethodDoc` - Method doc retrieval
- `TestFormatHoverMarkdown` - Hover markdown formatting
- `TestFormatMethodHover` - Method hover formatting

### test_predefinition.py

- `TestTokenTypes` - Semantic token types
- `TestTokenModifiers` - Token modifiers
- `TestKeywords` - Python/SageMath keywords
- `TestFunctions` - SageMath function definitions
- `TestClasses` - SageMath class definitions

## Writing New Tests

Use the fixtures defined in `conftest.py`:

```python
def test_example(mock_document, position):
    doc = mock_document("x = 5\ny = 10")
    pos = position(0, 0)
    # Test logic here
```

Available fixtures:
- `mock_document` - Factory for creating mock TextDocument objects
- `mock_ls` - Mock language server
- `simple_document` - Pre-configured simple document

- `class_document` - Document with class definition
- `sagemath_document` - Document with SageMath code
- `diagnostic_document` - Document with diagnostic issues
- `empty_document` - Empty document
- `position` - Factory for creating Position objects
- `sample_tokens` - Sample token list
