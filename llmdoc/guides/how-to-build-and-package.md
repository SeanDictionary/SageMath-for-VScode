# How to Build and Package

1. **Compile TypeScript**: Run `npm run compile` to generate JavaScript output in `out/` directory. Uses TypeScript compiler configuration (`tsconfig.json`) with Node16 module system.
2. **Lint Code**: Run `npm run lint` to check code quality via ESLint (`.eslintrc.json`). Fix issues automatically with `npm run lint:fix`.
3. **Run Tests**: Execute `npm test` to run integration tests. This compiles TypeScript first via `pretest` hook, then runs tests via `@vscode/test-electron` framework (`src/test/runTest.ts`).
4. **Package Extension**: Run `npm run package` to create a `.vsix` file using `@vscode/vsce`. This excludes source files per `.vscodeignore`.
5. **Publish**: Use `npm run publish` to publish directly to VS Code Marketplace (requires `VSCE_PAT`).

## Local Build Verification

```bash
npm ci
npm run compile
npm run lint
npm test
npm run package
```

This generates `sagemath-for-vscode-{version}.vsix` ready for installation.
