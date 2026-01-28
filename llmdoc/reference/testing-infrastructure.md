# Testing Infrastructure Reference

## 1. Core Summary

Comprehensive testing framework covering both VS Code extension (TypeScript) and LSP server (Python) using `@vscode/test-electron` and `pytest` with `uv` package manager.

## 2. Source of Truth

### VS Code Extension Tests
- **Test Runner**: `src/test/runTest.ts` - Entry point launching VS Code Extension Development Host
- **Test Index**: `src/test/suite/index.ts` - Mocha test runner configuration
- **Test Suites**:
  - `extension.test.ts` - Basic activation and command registration
  - `extension.test.extended.ts` - Extended functionality tests
  - `lsp.test.ts` - LSP client initialization
  - `lsp.e2e.test.ts` - End-to-end LSP communication
  - `lsp.integration.test.ts` - LSP integration scenarios
  - `sageDiscovery.test.ts` - SageMath installation discovery
- **Helpers**: `src/test/suite/lsp-helpers.ts` - Fixtures and utility functions

### Python LSP Server Tests
- **Pytest Config**: `src/server/pyproject.toml:20-30` - Test configuration with markers and coverage
- **Test Fixtures**: `src/server/tests/conftest.py` - Mock documents and server instances
- **Test Suites**:
  - `test_lsp.py` - LSP server lifecycle and initialization
  - `test_lsp_protocol.py` - LSP protocol message handling
  - `test_code_actions.py` - Code action providers
  - `test_documentation.py` - Hover documentation
  - `test_symbols.py` - Symbol resolution (go-to-definition)
  - `test_utils.py` - Tokenization and classification utilities
  - `test_predefinition.py` - SageMath standard library definitions

## Execution

**VS Code Tests**: `npm test` (runs TypeScript tests via `@vscode/test-electron`)

**Python Tests**:
- `npm run test:python:setup` - Initial setup with `uv`
- `npm run test:python` - Run pytest tests
- `npm run test:python:cov` - Run with coverage report

**All Tests**: `npm run test:all` (sequential execution)

## Test Coverage

VS Code tests verify: Extension activation, command registration, language configuration, settings, LSP client startup

Python tests verify: Tokenization, semantic classification, LSP protocol compliance, SageMath definitions
