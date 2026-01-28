# SageMath For VScode

![Release](https://img.shields.io/github/v/release/SeanDictionary/SageMath-for-VScode) ![Platform](https://img.shields.io/badge/platform-Windows%20|%20Linux%20|%20macOS-green) ![License](https://img.shields.io/github/license/SeanDictionary/SageMath-for-VScode) ![GitHub repo size](https://img.shields.io/github/repo-size/SeanDictionary/SageMath-for-VScode) ![GitHub last commit](https://img.shields.io/github/last-commit/SeanDictionary/SageMath-for-VScode) ![Python](https://img.shields.io/badge/python-3.10%2B-blue)

<div align="center">English | <a href="https://github.com/SeanDictionary/SageMath-for-VScode/blob/main/docs/README-zh-CN.md">中文</a></div>

---

## What is this?

A full-featured [SageMath](https://www.sagemath.org/) extension for Visual Studio Code with complete Language Server Protocol (LSP) support, providing intelligent code assistance for mathematical computing.

## Features

### Language Server Protocol (LSP)

- **Code Completion** - Context-aware suggestions for SageMath functions, classes, methods, keywords, and user-defined symbols
- **Hover Documentation** - Detailed documentation on hover with examples and parameter info
- **Signature Help** - Parameter hints when typing function arguments
- **Diagnostics** - Real-time syntax checking with warnings and hints
- **Go to Definition** - Navigate to symbol definitions in your code
- **Find References** - Find all usages of a symbol in the current file
- **Semantic Highlighting** - Enhanced syntax coloring based on SageMath's standard library
- **Document Symbols** - Outline view showing functions, classes, and variables
- **Folding Ranges** - Fold/unfold code blocks, comments, and docstrings
- **Rename Symbol** - Rename user-defined symbols across the document
- **Code Actions** - Quick fixes for common issues (typos, missing imports, etc.)
- **Inlay Hints** - Optional inline type hints for variables

### Code Snippets (70+)

Built-in snippets for common SageMath patterns:

| Category | Snippets |
|----------|----------|
| **Number Theory** | `factor`, `gcd`, `xgcd`, `crt`, `invmod`, `powmod`, `dlog` |
| **Linear Algebra** | `mat`, `lll`, `bkz`, `kernel`, `eigen`, `jordan`, `smith` |
| **Cryptography** | `rsa`, `wiener`, `hastad`, `pohlig`, `copper` |
| **Elliptic Curves** | `ec`, `ecpoint`, `ecrand` |
| **Algebra** | `polyring`, `gf`, `ideal`, `groebner` |
| **Symbolic** | `var`, `solve`, `diff`, `integrate`, `limit`, `taylor` |
| **Plotting** | `plot`, `paraplot`, `plot3d` |

Type the prefix and press `Tab` to expand snippets.

### Code Execution

- **Run SageMath** (`F5`) - Execute `.sage` files
- **Run Selected Code** (`Shift+Enter`) - Execute selected code in interactive mode
- **Conda Integration** - Switch between Conda environments with status bar selector
- **Auto Cleanup** - Automatically remove generated `.sage.py` files after execution

### Editor Support

- **Syntax Highlighting** - Full TextMate grammar for SageMath code
- **Comment Shortcuts** - Hotkeys for line (`Ctrl+/`) and block comments
- **Docstring Generator** (`Ctrl+Shift+/`) - Auto-generate function docstrings
- **Documentation Lookup** (`Ctrl+Shift+D`) - Search official SageMath docs
- **Cross-Platform** - Works on Windows, Linux, and macOS

### Configuration

#### Basic Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `sage.path` | Path to SageMath executable | `sage` |
| `sage.condaEnvPath` | Conda environment path | (empty) |
| `LSP.useSageMathLSP` | Enable/disable LSP features | `true` |
| `LSP.LSPLogLevel` | LSP log level | `info` |

#### Completion Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `completion.enabled` | Enable code completion | `true` |
| `completion.maxItems` | Maximum completion items | `100` |
| `completion.showSnippets` | Show snippets in completion | `true` |
| `completion.showUserSymbols` | Show user-defined symbols | `true` |

#### Diagnostics Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `diagnostics.enabled` | Enable diagnostics | `true` |
| `diagnostics.undefinedCheck` | Check undefined variables | `true` |
| `diagnostics.indentationCheck` | Check mixed indentation | `true` |
| `diagnostics.maxProblems` | Maximum problems to report | `100` |

#### Run Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `run.autoSave` | Auto-save before running | `true` |
| `run.clearTerminal` | Clear terminal before run | `false` |
| `run.showExecutionTime` | Show execution time | `false` |

#### Inlay Hints

| Setting | Description | Default |
|---------|-------------|---------|
| `inlayHints.enabled` | Enable inlay hints | `false` |
| `inlayHints.showTypes` | Show inferred types | `true` |

### Commands

| Command | Keybinding | Description |
|---------|------------|-------------|
| Run SageMath File | `F5` | Run the current `.sage` file |
| Run Selected Code | `Shift+Enter` | Execute selected code interactively |
| Open Documentation | `Ctrl+Shift+D` | Search SageMath documentation |
| Insert Docstring | `Ctrl+Shift+/` | Generate docstring template |
| Restart LSP | - | Restart the language server |
| Select Conda Environment | - | Choose Conda environment |
| Show LSP Status | - | Display LSP server status |
| **Setup Wizard** | - | Interactive setup for first-time users |
| **Check SageMath Status** | - | Verify SageMath installation |
| **Discover Installations** | - | Auto-detect SageMath installations |
| **Installation Guide** | - | Platform-specific install instructions |

### Installation & Setup

The extension includes an **intelligent setup wizard** that helps you configure SageMath:

1. **First-Run Detection**: On first launch, if SageMath is not detected, the extension offers to run the setup wizard
2. **Auto-Discovery**: Automatically searches for SageMath in:
   - System PATH
   - Conda/Mamba environments
   - Common installation paths (platform-specific)
   - WSL (Windows only)
3. **Installation Guide**: Provides platform-specific installation instructions:
   - **Windows**: Conda (recommended), WSL, or binary installer
   - **macOS**: Homebrew (recommended), Conda, or app bundle
   - **Linux**: System package manager (recommended) or Conda

To manually run the setup wizard, use the command palette (`Ctrl+Shift+P`) and search for "SageMath: Setup Wizard".

### Extensibility

The LSP uses `predefinition.py` for SageMath standard library definitions. You can modify this file to add custom functions, classes, and methods for enhanced completion and highlighting.

## Requirements

- **SageMath** installed via [Conda](https://doc.sagemath.org/html/en/installation/conda.html) (recommended)
- **Python 3.10+** (included with SageMath)
- **VS Code 1.100.0+**

> **Note:** The LSP server requires a Conda environment with SageMath. On first activation, the extension will prompt you to select your Conda environment and automatically create a Python venv for the LSP server.

## Installation

### From VS Code Marketplace

1. Open VS Code and go to Extensions (`Ctrl+Shift+X`)
2. Search for "SageMath for VScode"
3. Click **Install**
4. Open a `.sage` file to activate the extension
5. When prompted, select your SageMath Conda environment

### From GitHub

1. Download the `.vsix` file from the [Releases page](https://github.com/SeanDictionary/SageMath-for-VScode/releases)
2. In VS Code, open Command Palette (`Ctrl+Shift+P`) and run `Extensions: Install from VSIX...`
3. Select the downloaded `.vsix` file

## Changelog

See [CHANGELOG.md](https://github.com/SeanDictionary/SageMath-for-VScode/blob/main/CHANGELOG.md) for details.

## Contributes

If you want to contribute to this project, you can fork the repository and create a pull request. You can also report issues or suggest features by opening an issue on the GitHub repository. See [CONTRIBUTING.md](https://github.com/SeanDictionary/SageMath-for-VScode/blob/main/docs/CONTRIBUTING.md) for more details.

## License

This project is licensed under the AGPL-3.0 License. See the [LICENSE](https://github.com/SeanDictionary/SageMath-for-VScode/blob/main/LICENSE) file for details.
