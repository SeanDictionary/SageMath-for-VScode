# Change Log

All notable changes to the "sagemath" extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

-   Add icon
-   support more functions and classes in `predefinition.py`

### Changed

-   wrap start lsp function

### Fixed

-   auto-installing python dependencies instead of venv

## [0.0.3] - 2025-06-25

### Added

-   Select Conda environment for SageMath
-   using venv for lsp

### Fixed

-   change package.json devDependencies to dependencies to package and publish the extension

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
