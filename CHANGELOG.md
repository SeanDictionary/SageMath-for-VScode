# Change Log

All notable changes to the "sagemath" extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

-  Auto-create Python venv for LSP. It fix errors coused by PEP 668 on new Linux distributions like Arch, Ubuntu 24.04, etc.

### Changed

-  Using the default terminal in vscode to run sagemath. It supports zsh, bash, cmd, pwsh, etc.

### Removed

-  Remove the unuseful dependences

## [1.0.0] - 2025-07-04

-  Release 1.0.0

### Test

-  Test the extension on WSL2

### Changed

-  Update readme

## [0.0.4] - 2025-07-04

### Added

-   Add icon
-   Support more functions and classes in `predefinition.py`

### Changed

-   Wrap start lsp function

### Fixed

-   Auto-installing python dependencies instead of venv

## [0.0.3] - 2025-06-25

### Added

-   Select Conda environment for SageMath
-   Using venv for lsp

### Fixed

-   Change package.json devDependencies to dependencies to package and publish the extension

## [0.0.2] - 2025-06-21

### Added

-   Command: restart LSP
-   Add tiny logging package in utils
-   Add settings to configure LSP log level
-   Add support for real-time LSP log level switching
-   Add basic semantic highlighting for SageMath

## [0.0.1] - 2025-06-13

### Added

-   Initial release
-   Support basic partly syntax highlighting for SageMath
-   Add hotkey for line comment and block comment
-   Add command to run SageMath
-   Bind F5 to run SageMath
-   Add button to run SageMath in the status bar
-   Add settings to configure SageMath path
