# SageMath For VScode

![Release](https://img.shields.io/github/v/release/SeanDictionary/SageMath-for-VScode) ![Platform](https://img.shields.io/badge/platform-Linux-green) ![License](https://img.shields.io/github/license/SeanDictionary/SageMath-for-VScode) ![GitHub repo size](https://img.shields.io/github/repo-size/SeanDictionary/SageMath-for-VScode) ![GitHub last commit](https://img.shields.io/github/last-commit/SeanDictionary/SageMath-for-VScode) ![Python](https://img.shields.io/badge/python-3.10%2B-blue)

<div align="center">English | <a href="https://github.com/SeanDictionary/SageMath-for-VScode/blob/main/docs/README-zh-CN.md">中文</a></div>

---

## What is this?

It's a extension for [SageMath](https://www.sagemath.org/) that provides syntax highlighting, code execution, and other features for Visual Studio Code.

I wish to make it a full-featured SageMath extension, especially for SageMath's LSP (Language Server Protocol) support. But obviously it'll be a hard work. Welcome to contribute and suggest!

## Features

-   Syntax highlighting for SageMath code
-   Basic Semantic highlighting for SageMath code (there are still some bugs, you can see [known bugs file](https://github.com/SeanDictionary/SageMath-for-VScode/blob/main/docs/SemanticHighlighting-en.md) for details)
-   Support F5, command and buttom to run SageMath file
-   Support hotkey for line comment and block comment
-   Support conda environment switching
-   Semantic highlighting rely on `perdefinition.py` for SageMath Std Library, you can modify this file to add more semantic highlighting support
-   Auto-remove `.sage.py` files after running SageMath

## Changelog

See [CHANGELOG.md](https://github.com/SeanDictionary/SageMath-for-VScode/blob/main/CHANGELOG.md) for details.

## Usage

The extension **has released** on the Visual Studio Code Marketplace yet. You can install it from GitHub or the Visual Studio Code Marketplace.

### From GitHub

1. Download the `.vsix` file from latest pre-release or release from the [Releases page](https://github.com/SeanDictionary/SageMath-for-VScode/releases)
2. Drag the `.vsix` file into the Visual Studio Code window, or use the command palette (`Ctrl+Shift+P`) and type `Extensions: Install from VSIX...`, then select the downloaded `.vsix` file.

### From VScode Marketplace

1. Open Visual Studio Code
2. Go to Extensions view by clicking on the Extensions icon in the Activity Bar on the side of the window or pressing `Ctrl+Shift+X`.
3. Search for "SageMath for VScode"
4. Click on the "Install" button for the extension named "SageMath for VScode" by SeanDictionary.
5. After installation, you may need to reload the window or restart Visual Studio Code for the extension to take effect.
6. Open a SageMath file (with `.sage` extension) to start using the extension.

## Contributes

If you want to contribute to this project, you can fork the repository and create a pull request. You can also report issues or suggest features by opening an issue on the GitHub repository. See [CONTRIBUTING.md](https://github.com/SeanDictionary/SageMath-for-VScode/blob/main/docs/CONTRIBUTING.md) for more details.

## License

This project is licensed under the AGPL-3.0 License. See the [LICENSE](https://github.com/SeanDictionary/SageMath-for-VScode/blob/main/LICENSE) file for details.