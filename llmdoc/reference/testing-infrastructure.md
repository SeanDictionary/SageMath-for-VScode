# Testing Infrastructure Reference

## 1. Core Summary

Integration testing framework using `@vscode/test-electron` to verify extension activation, command registration, language configuration, and settings within a VS Code environment.

## 2. Source of Truth

- **Test Runner**: `src/test/runTest.ts` - Entry point that launches VS Code and runs test suite
- **Test Suite**: `src/test/suite/extension.test.ts` - Integration tests for extension behavior
- **Test Config**: `package.json:162-163` - `pretest` and `test` npm scripts
- **Framework**: `@vscode/test-electron` - Official VS Code extension testing framework

## Test Structure

**runTest.ts** (`src/test/runTest.ts`):
- Resolves extension development path (project root)
- Resolves test runner path (`src/test/suite/index`)
- Invokes `runTests()` to download VS Code and execute tests

**extension.test.ts** (`src/test/suite/extension.test.ts`):
- Suite 1: Extension Test Suite
  - Extension presence verification
  - Activation verification
  - Command registration (`runSageMath`, `restartLSP`, `selectCondaEnv`)
  - Language configuration (`sagemath` language ID)
  - Configuration settings (`sage.path`, `sage.condaEnvPath`, `LSP.useSageMathLSP`, `LSP.LSPLogLevel`)
- Suite 2: SageMath Language Support
  - `.sage` file extension recognition

## Execution

**Local**: Run `npm test` (compiles TypeScript first via `pretest` hook)

**CI**: GitHub Actions runs `xvfb-run -a npm test` on Linux (`.github/workflows/ci.yml:37`)

## TypeScript Configuration

Test files use `tsconfig.json` with `strict: true`, `module: "Node16"`, and `types: ["node", "mocha"]`.
