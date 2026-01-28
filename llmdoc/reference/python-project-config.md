# Python LSP Server Configuration Reference

## 1. Core Summary

Modern Python project configuration using `pyproject.toml` for dependency management, pytest configuration, and uv package manager for fast, reproducible builds. The LSP server requires Python >=3.10 and uses pygls for LSP protocol implementation.

## 2. Source of Truth

- **Project Config**: `src/server/pyproject.toml` - Python project metadata, dependencies, and tool configuration
- **Lock File**: `src/server/uv.lock` - uv lock file for reproducible dependency resolution
- **Pytest Config**: `src/server/pytest.ini` - Pytest test discovery and execution settings
- **Requirements**: `src/server/requirements.txt` - Legacy requirements file for backward compatibility
- **Version Sync**: `package.json:333-334` - npm scripts for version synchronization

## Project Structure

**Name**: `sagemath-lsp`
**Version**: Synced with `package.json` via `version:sync` script
**Python Required**: >=3.10

## Dependencies

### Runtime Dependencies (`pyproject.toml:7-11`)

- `pygls==1.3.1` - Python LSP framework
- `lsprotocol>=2023.0.0,<2024.0.0` - LSP protocol types
- `attrs>=23.1.0` - Class decorators and metaprogramming

### Development Dependencies (`pyproject.toml:13-18`)

- `pytest>=8.0.0` - Test framework
- `pytest-mock>=3.12.0` - Mocking utilities
- `pytest-cov>=4.1.0` - Coverage reporting

## Test Configuration

**Pytest Settings** (`pyproject.toml:20-30`):
- Test paths: `["tests"]`
- File pattern: `test_*.py`
- Markers: `slow`, `integration`
- Warnings: Ignore `DeprecationWarning`
- Coverage: Configured in `[tool.coverage.run]` section

## Package Manager

**uv** - Fast Python package installer and resolver (replaces pip for development)

- **Setup**: `npm run test:python:setup` (runs `uv sync --dev`)
- **Run Tests**: `npm run test:python` (runs `uv run pytest tests/ -v`)
- **Lock File**: `uv.lock` ensures reproducible builds across environments

## Version Management

The LSP server version is kept in sync with the VS Code extension version:

- **Check**: `npm run version:check` - Verifies `package.json` and `pyproject.toml` versions match
- **Sync**: `npm run version:sync` - Updates `pyproject.toml` version from `package.json`

This ensures consistent versioning across the entire project.
