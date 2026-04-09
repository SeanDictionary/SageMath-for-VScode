# Change Log

All notable changes to the "SageMath for VScode" extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-xx-xx

### Added

- Add `sagemath-for-vscode.sage.condaPath` setting so Conda can be located even when `conda` is not available on the default `PATH`
- Add a `Global Env` option to the Conda environment picker
- Add an LSP status item in the status bar
- Add click-to-open access from the LSP status item to the shared `SageMath Language Server` output channel

### Changed

- Rename the SageMath executable setting key to `sagemath-for-vscode.sage.sagePath`
- Rework LSP lifecycle handling so start, stop, and restart follow the same control flow
- Reuse a single LSP output channel across restarts
- Run SageMath from the current file directory again to keep the terminal working directory correct

### Fixed

- Fix `conda: not found` errors by allowing a custom Conda executable path
- Fix blocking retry behavior when `condaEnvPath` is empty
- Fix the Conda environment selection flow, including support for keeping the previous setting when selection is cancelled
- Fix environment display and global-environment handling in the status bar
- Fix LSP restart behavior after environment and log-level changes
- Fix LSP status feedback for starting, running, stopped, disabled, and error states

### Removed

- Remove the unused `npm test` script

## [2.0.2-beta] - 2026-02-24

This version is a beta release using the Python package [sage-lsp](https://pypi.org/project/sage-lsp/) to start the LSP server. It is otherwise the same as [2.0.1].

### Added

- Add text for Env selection button
- Add Github Actions for publishing and generate release

### Changed

- Using python package [sage-lsp](https://pypi.org/project/sage-lsp/) to start LSP server, which is more stable and faster than the old method.

### Fixed

- Support SageMath 10.8 and later

## [2.0.0] - 2025-11-13

### Added

- File focus option when running SageMath in terminal

### Fixed

- Fix conda env path empty and selection bugs

### Changed

- Using sage global env instead of venv to be suitable for LSP

---

## [1.1.2] - 2025-11-05

### Fixed

- Fix [#1](https://github.com/SeanDictionary/SageMath-for-VScode/issues/1)

### Changed

- Using sage -python to start LSP server [#2](https://github.com/SeanDictionary/SageMath-for-VScode/issues/2)

### Added

- Add .vscode for development

---

## [1.1.1] - 2025-07-24

### Fixed

- Fix highlight bug in `for` sentences.

### Changed

- Update `predefinition.py`.
- Add `cd` command before running SageMath.

---

## [1.1.0] - 2025-07-09

### Added

- Auto-create Python venv for LSP. It fix errors coused by PEP 668 on new Linux distributions like Arch, Ubuntu 24.04, etc.

### Changed

- Using the default terminal in vscode to run sagemath. It supports zsh, bash, cmd, pwsh, etc.

### Removed

- Remove the unuseful dependences

---

## [1.0.0] - 2025-07-04

- Release 1.0.0

### Test

- Test the extension on WSL2

### Changed

- Update readme

---

## [0.0.4] - 2025-07-04

### Added

- Add icon
- Support more functions and classes in `predefinition.py`

### Changed

- Wrap start lsp function

### Fixed

- Auto-installing python dependencies instead of venv

---

## [0.0.3] - 2025-06-25

### Added

- Select Conda environment for SageMath
- Using venv for lsp

### Fixed

- Change package.json devDependencies to dependencies to package and publish the extension

---

## [0.0.2] - 2025-06-21

### Added

- Command: restart LSP
- Add tiny logging package in utils
- Add settings to configure LSP log level
- Add support for real-time LSP log level switching
- Add basic semantic highlighting for SageMath

---

## [0.0.1] - 2025-06-13

### Added

- Initial release
- Support basic partly syntax highlighting for SageMath
- Add hotkey for line comment and block comment
- Add command to run SageMath
- Bind F5 to run SageMath
- Add button to run SageMath in the status bar
- Add settings to configure SageMath path
