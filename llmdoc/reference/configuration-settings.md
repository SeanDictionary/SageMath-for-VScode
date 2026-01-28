# Configuration Settings Reference

## 1. Core Summary

Extension configuration schema defining all user-customizable settings for SageMath language support, organized into six categories: SageMath execution, LSP server, code completion, diagnostics, run behavior, hover documentation, and inlay hints.

## 2. Source of Truth

- **Primary Config**: `package.json:144-277` - Complete configuration schema with defaults and descriptions
- **Extension Code**: `src/extension.ts` - Configuration consumption and command logic
- **LSP Server**: `src/server/lsp.py` - LSP configuration handling

## Configuration Categories

### SageMath Execution (`sagemath-for-vscode.sage.*`)

- **sage.path** (string, default: `"sage"`): Path to SageMath executable
- **sage.condaEnvPath** (string, default: `""`): Conda environment name for SageMath execution

### LSP Server (`sagemath-for-vscode.LSP.*`)

- **useSageMathLSP** (boolean, default: `true`): Enable/disable Language Server Protocol
- **LSPLogLevel** (enum: `"error"`|`"warn"`|`"info"`|`"debug"`, default: `"info"`): Server log verbosity

### Code Completion (`sagemath-for-vscode.completion.*`)

- **enabled** (boolean, default: `true`): Enable/disable code completion
- **maxItems** (number, default: `100`, range: 10-500): Maximum completion suggestions
- **showSnippets** (boolean, default: `true`): Include code snippets in suggestions
- **showUserSymbols** (boolean, default: `true`): Include user-defined symbols in completion

### Diagnostics (`sagemath-for-vscode.diagnostics.*`)

- **enabled** (boolean, default: `true`): Enable/disable code diagnostics
- **undefinedCheck** (boolean, default: `true`): Warn on undefined variables
- **indentationCheck** (boolean, default: `true`): Detect mixed tabs/spaces
- **maxProblems** (number, default: `100`, range: 10-1000): Maximum diagnostic problems

### Run Behavior (`sagemath-for-vscode.run.*`)

- **autoSave** (boolean, default: `true`): Auto-save before execution
- **clearTerminal** (boolean, default: `false`): Clear terminal before running
- **showExecutionTime** (boolean, default: `false`): Display execution time after run

### Hover Documentation (`sagemath-for-vscode.hover.*`)

- **showExamples** (boolean, default: `true`): Show usage examples in hover
- **showDocLink** (boolean, default: `true`): Link to official SageMath docs in hover

### Inlay Hints (`sagemath-for-vscode.inlayHints.*`)

- **enabled** (boolean, default: `false`): Enable inline type hints
- **showTypes** (boolean, default: `true`): Display inferred types as hints
