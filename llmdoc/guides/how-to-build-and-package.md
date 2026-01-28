# How to Build and Package

1. **Install Dependencies**: Run `npm ci` for clean installation of Node dependencies. For Python LSP server, run `npm run test:python:setup` to install test dependencies via uv.
2. **Check Formatting**: Run `npm run format:check` to verify code formatting with Prettier (`.prettierrc.json`). Auto-fix with `npm run format`.
3. **Lint Code**: Run `npm run lint` to check code quality via ESLint (`.eslintrc.json`). Fix issues automatically with `npm run lint:fix`.
4. **Compile TypeScript**: Run `npm run compile` to generate JavaScript output in `out/` directory. Uses TypeScript compiler configuration (`tsconfig.json`) with Node16 module system.
5. **Run Tests**: Execute `npm test` for TypeScript integration tests. Run `npm run test:python` for Python LSP server tests. Run `npm run test:all` for complete test suite.
6. **Package Extension**: Run `npm run package` to create a `.vsix` file using `@vscode/vsce`. This excludes source files per `.vscodeignore`.
7. **Publish**: Use `npm run publish` to publish directly to VS Code Marketplace (requires `VSCE_PAT`).

## Version Management

Before packaging, ensure version consistency between `package.json` and `src/server/pyproject.toml`:

- **Check versions**: Run `npm run version:check` to verify versions match
- **Sync versions**: Run `npm run version:sync` to update `pyproject.toml` with `package.json` version

## Full Build Verification

```bash
npm ci
npm run format:check
npm run lint
npm run compile
npm run test:all
npm run version:check
npm run package
```

This generates `sagemath-for-vscode-{version}.vsix` ready for installation.
