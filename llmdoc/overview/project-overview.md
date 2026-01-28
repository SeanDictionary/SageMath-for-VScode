# SageMath for VS Code

## 1. Identity

- **What it is:** A VS Code extension providing language support for SageMath (`.sage` files).
- **Purpose:** Enables mathematical computing in VS Code with syntax highlighting, semantic analysis, and code execution capabilities.

## 2. High-Level Description

A TypeScript-based VS Code extension that implements a client-server architecture using the Language Server Protocol (LSP). The extension provides three core capabilities: (1) TextMate-based syntax highlighting inherited from Python with custom comment patterns, (2) LSP-based semantic highlighting through a Python server using pygls that recognizes 150+ SageMath functions and 30+ classes, and (3) terminal-based code execution with Conda environment integration. The architecture separates concerns between the TypeScript client (extension logic, command handling, LSP client management) and the Python server (lexical/semantic analysis, standard library knowledge base).
