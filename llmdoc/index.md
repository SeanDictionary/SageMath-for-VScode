# SageMath for VS Code - Documentation Index

This index provides a complete navigation map of the project documentation, organized for efficient LLM retrieval.

---

## Overview

- [`project-overview`](overview/project-overview.md) - High-level project identity and architecture summary

---

## Architecture (LLM Retrieval Map)

### Core Extension Architecture

- [`extension-overview`](architecture/extension-overview.md) - Extension subsystems, command registration, and LSP client management
- [`extension-lifecycle`](architecture/extension-lifecycle.md) - Activation flow, command registration, and LSP initialization sequence
- [`terminal-integration`](architecture/terminal-integration.md) - Terminal management, Conda environment activation, and SageMath file execution

### Language Server Protocol (LSP)

- [`lsp-overview`](architecture/lsp-overview.md) - Python-based LSP server architecture and single-pass analysis pipeline
- [`lexical-analysis`](architecture/lexical-analysis.md) - Tokenization engine using regex patterns and delta encoding
- [`semantic-analysis`](architecture/semantic-analysis.md) - Single-pass classification algorithm for symbols, functions, classes, and variables
- [`semantic-tokens`](architecture/semantic-tokens.md) - Token encoding format and LSP transmission protocol

### Syntax Highlighting

- [`syntax-highlighting-overview`](architecture/syntax-highlighting-overview.md) - TextMate grammar integration and semantic highlighting coordination
- [`textmate-grammar`](architecture/textmate-grammar.md) - TextMate grammar structure for `.sage` file syntax highlighting

---

## Guides (Step-by-Step Instructions)

### Development Setup

- [`how-to-setup-development`](guides/how-to-setup-development.md) - Clone repository, install dependencies, and launch Extension Development Host
- [`how-to-build-and-package`](guides/how-to-build-and-package.md) - Build TypeScript extension and package VSIX file

### LSP and Semantic Analysis

- [`how-lsp-client-works`](guides/how-lsp-client-works.md) - LSP client initialization, server startup, and request-response communication flow
- [`how-semantics-work`](guides/how-semantics-work.md) - Token classification pipeline from lexical analysis to semantic highlighting

### Extension Development

- [`how-to-extend-commands`](guides/how-to-extend-commands.md) - Add new commands to `package.json` and implement handlers in `extension.ts`
- [`how-to-add-sagemath-definitions`](guides/how-to-add-sagemath-definitions.md) - Extend SageMath standard library definitions in `predefinition.py`

---

## Reference (Source of Truth)

### Conventions and Standards

- [`coding-conventions`](reference/coding-conventions.md) - TypeScript and Python code style, naming patterns, and architectural constraints
- [`git-conventions`](reference/git-conventions.md) - Branch naming, commit message format, and pull request workflow

### Configuration and Build

- [`npm-scripts`](reference/npm-scripts.md) - Available npm scripts for building, watching, testing, and packaging
- [`ci-workflows`](reference/ci-workflows.md) - GitHub Actions workflow definitions for automated testing and deployment
- [`code-quality-tools`](reference/code-quality-tools.md) - ESLint, Prettier, and EditorConfig configuration for code quality enforcement
- [`testing-infrastructure`](reference/testing-infrastructure.md) - Integration testing setup using @vscode/test-electron

### SageMath Language Support

- [`sagemath-token-types`](reference/sagemath-token-types.md) - LSP token types and modifiers (14 types, 6 modifiers) with encoding format
- [`sagemath-standard-library`](reference/sagemath-standard-library.md) - Predefined SageMath functions (150+) and classes (30+) for semantic recognition

---

## Documentation Maintenance

This index is automatically synchronized with the `/llmdoc` directory structure. When adding new documentation:

1. Place files in appropriate category directory (`overview/`, `guides/`, `architecture/`, `reference/`)
2. Follow the content format specified in `/llmdoc/index.md`
3. Update this index with the new document link and brief description
4. Delete temporary scout reports from `/llmdoc/agent/` after documentation is complete

---

**Last Updated:** 2026-01-28
**Documentation Version:** 1.1
**Project:** SageMath for VS Code v1.3.0
