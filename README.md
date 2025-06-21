# SageMath For VScode

![Release](https://img.shields.io/github/v/release/SeanDictionary/SageMath-for-VScode) ![Platform](https://img.shields.io/badge/platform-Linux-green) ![License](https://img.shields.io/github/license/SeanDictionary/SageMath-for-VScode) ![GitHub top language](https://img.shields.io/github/languages/top/SeanDictionary/SageMath-for-VScode) ![GitHub last commit](https://img.shields.io/github/last-commit/SeanDictionary/SageMath-for-VScode)

<div align="center">English | <a href="./readmes/README-zh-CN.md">中文</a></div>

---

## What is this?

It's a extension for [SageMath](https://www.sagemath.org/) that provides syntax highlighting, code execution, and other features for Visual Studio Code.

I wish to make it a full-featured SageMath extension, especially for SageMath's LSP (Language Server Protocol) support. But obviously it'll be a hard work. Welcome to contribute and suggest!

## Features

-   Syntax highlighting for SageMath code
-   Basic Semantic highlighting for SageMath code (there are still some bugs, you can see [known bugs file](./readmes/SemanticHighlighting-en.md) for details)
-   Support F5, command and buttom to run SageMath file
-   Support hotkey for line comment and block comment

## Chagelog

See [CHANGELOG.md](./CHANGELOG.md) for details.

## Usage

The extension **isn't released** on the Visual Studio Code Marketplace yet, so you need to download it from github and install personaly.

### From GitHub

1. Download the latest pre-release or release from the [Releases page](https://github.com/SeanDictionary/SageMath-for-VScode/releases)
2. Open path `~/.vscode/extensions/` in your file manager.
3. Extract the downloaded file to this directory.

### ~~From VScode Marketplace~~ Not supported yet

1. Open Visual Studio Code
2. Go to Extensions view by clicking on the Extensions icon in the Activity Bar on the side of the window or pressing `Ctrl+Shift+X`.
3. Search for "SageMath for VScode"
4. Click on the "Install" button for the extension named "SageMath for VScode" by SeanDictionary.
5. After installation, you may need to reload the window or restart Visual Studio Code for the extension to take effect.
6. Open a SageMath file (with `.sage` extension) to start using the extension.

## Contributes

If you want to contribute to this project, you can fork the repository and create a pull request. You can also report issues or suggest features by opening an issue on the GitHub repository.

## License

This project is licensed under the AGPL-3.0 License. See the [LICENSE](./LICENSE) file for details.