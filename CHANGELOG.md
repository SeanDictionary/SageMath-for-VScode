# Change Log

All notable changes to the "sagemath" extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-01-28

### Added
- **Code Snippets**: 70+ code snippets for common SageMath patterns
  - Number theory: `factor`, `gcd`, `xgcd`, `crt`, `invmod`, `powmod`, `dlog`
  - Linear algebra: `mat`, `lll`, `bkz`, `kernel`, `eigen`, `jordan`
  - Cryptography: `rsa`, `wiener`, `hastad`, `pohlig`, `copper`
  - Elliptic curves: `ec`, `ecpoint`, `ecrand`
  - Symbolic: `var`, `solve`, `diff`, `integrate`, `limit`, `taylor`
  - And many more...

- **New Commands**:
  - `Run Selected Code` (Shift+Enter) - Execute selected code in interactive SageMath
  - `Open SageMath Documentation` (Ctrl+Shift+D) - Search official docs
  - `Insert Docstring Template` (Ctrl+Shift+/) - Generate docstring for functions
  - `Show LSP Status` - Display LSP server status and features

- **Enhanced Auto-Completion**:
  - User-defined symbols (functions, classes, variables) now appear in completions
  - Symbols from current file are prioritized
  - Type inference for common SageMath types (Matrix, EllipticCurve, etc.)
  - Completion resolve provider for lazy documentation loading

- **Document Symbols (Outline View)**:
  - Functions, classes, and variables appear in the outline
  - SageMath-specific patterns recognized (e.g., `R.<x> = PolynomialRing(...)`)
  - Symbolic variables from `var('x y z')` detected

- **Folding Ranges**:
  - Fold functions, classes, loops, conditionals
  - Fold comment blocks and docstrings

- **Code Actions (Quick Fixes)**:
  - Add missing imports for common modules
  - Fix typos with "Did you mean..." suggestions
  - Convert tabs to spaces
  - Fix assignment in condition (`=` → `==`)
  - Generate docstring template

- **Rename Symbol**:
  - Rename user-defined symbols across the document
  - Validation prevents renaming keywords and builtins

- **Inlay Hints** (optional):
  - Show inferred types for variables
  - Enable in settings: `sagemath-for-vscode.inlayHints.enabled`

### Changed
- LSP version updated to 1.4.0
- Completion now includes `resolve_provider` for better performance
- Improved type inference for SageMath objects

### New Configuration Options
- `completion.enabled` - Enable/disable code completion
- `completion.maxItems` - Maximum completion items (default: 100)
- `completion.showSnippets` - Show snippets in completion
- `completion.showUserSymbols` - Show user-defined symbols
- `diagnostics.enabled` - Enable/disable diagnostics
- `diagnostics.undefinedCheck` - Check undefined variables
- `diagnostics.indentationCheck` - Check mixed indentation
- `diagnostics.maxProblems` - Maximum problems to report
- `run.autoSave` - Auto-save before running
- `run.clearTerminal` - Clear terminal before run
- `run.showExecutionTime` - Show execution time
- `hover.showExamples` - Show examples in hover
- `hover.showDocLink` - Show documentation links
- `inlayHints.enabled` - Enable inlay hints
- `inlayHints.showTypes` - Show type hints

## [1.1.3] - 2025-12-27

### Fixed

-   Fix [#4](https://github.com/SeanDictionary/SageMath-for-VScode/issues/4)

### Added

-   Auto-remove `.sage.py` files after running SageMath
-   Add something to `predefinition.py`

## [1.1.2] - 2025-11-05

### Fixed

-   Fix [#1](https://github.com/SeanDictionary/SageMath-for-VScode/issues/1) in [#3](https://github.com/SeanDictionary/SageMath-for-VScode/issues/3)

### Changed

-   Using sage -python to start LSP server [#2](https://github.com/SeanDictionary/SageMath-for-VScode/issues/2) in [#3](https://github.com/SeanDictionary/SageMath-for-VScode/issues/3)

### Added

-   Add .vscode for development

---

## [1.1.1] - 2025-07-24

### Fixed

-   Fix highlight bug in `for` sentences.

### Changed

-   Update `predefinition.py`.
-   Add `cd` command before running SageMath.

---

## [1.1.0] - 2025-07-09

### Added

-   Auto-create Python venv for LSP. It fix errors coused by PEP 668 on new Linux distributions like Arch, Ubuntu 24.04, etc.

### Changed

-   Using the default terminal in vscode to run sagemath. It supports zsh, bash, cmd, pwsh, etc.

### Removed

-   Remove the unuseful dependences

---

## [1.0.0] - 2025-07-04

-   Release 1.0.0

### Test

-   Test the extension on WSL2

### Changed

-   Update readme

---

## [0.0.4] - 2025-07-04

### Added

-   Add icon
-   Support more functions and classes in `predefinition.py`

### Changed

-   Wrap start lsp function

### Fixed

-   Auto-installing python dependencies instead of venv

---

## [0.0.3] - 2025-06-25

### Added

-   Select Conda environment for SageMath
-   Using venv for lsp

### Fixed

-   Change package.json devDependencies to dependencies to package and publish the extension

---

## [0.0.2] - 2025-06-21

### Added

-   Command: restart LSP
-   Add tiny logging package in utils
-   Add settings to configure LSP log level
-   Add support for real-time LSP log level switching
-   Add basic semantic highlighting for SageMath

---

## [0.0.1] - 2025-06-13

### Added

-   Initial release
-   Support basic partly syntax highlighting for SageMath
-   Add hotkey for line comment and block comment
-   Add command to run SageMath
-   Bind F5 to run SageMath
-   Add button to run SageMath in the status bar
-   Add settings to configure SageMath path
