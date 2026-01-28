# NPM Scripts Reference

## 1. Core Summary

Available npm scripts defined in `package.json`. These are the primary commands for development, testing, and packaging.

## 2. Source of Truth

- **Primary Code**: `package.json:316-334` - Script definitions
- **Related Guide**: `/llmdoc/guides/how-to-build-and-package.md` - Build workflow

## Available Scripts

### Build and Development

| Script | Command | Purpose |
|--------|---------|---------|
| `compile` | `tsc -p ./` | One-time TypeScript compilation |
| `watch` | `tsc -watch -p ./` | Incremental compilation with file watching |

### Code Quality

| Script | Command | Purpose |
|--------|---------|---------|
| `lint` | `eslint src --ext ts` | Check TypeScript code quality |
| `lint:fix` | `eslint src --ext ts --fix` | Auto-fix linting issues |
| `format` | `prettier --write "src/**/*.ts"` | Format code with Prettier |
| `format:check` | `prettier --check "src/**/*.ts"` | Verify code formatting |

### Testing

| Script | Command | Purpose |
|--------|---------|---------|
| `pretest` | `npm run compile` | Pre-test compilation hook |
| `test` | `node ./out/test/runTest.js` | Run VS Code extension tests |
| `test:python:setup` | `cd src/server && uv sync --dev` | Setup Python test environment |
| `test:python` | `cd src/server && uv run pytest tests/ -v` | Run Python LSP tests |
| `test:python:cov` | `cd src/server && uv run pytest tests/ -v --cov=. --cov-report=html` | Run tests with coverage |
| `test:all` | `npm run test:python && npm run test` | Run all tests (Python + TypeScript) |

### Packaging and Publishing

| Script | Command | Purpose |
|--------|---------|---------|
| `prepackage` | `npm run compile` | Pre-package compilation hook |
| `package` | `vsce package --no-yarn` | Create `.vsix` extension package |
| `package:check` | `vsce ls --no-yarn` | Verify package contents |
| `publish` | `vsce publish` | Publish to marketplace |

### Version Management

| Script | Command | Purpose |
|--------|---------|---------|
| `version:check` | `node -e "..."` | Verify `package.json` and `pyproject.toml` versions match |
| `version:sync` | `node -e "..."` | Sync `package.json` version to `pyproject.toml` |

## Dependencies

- **TypeScript Config**: `tsconfig.json` - Compiler options
- **ESLint Config**: `.eslintrc.json` - Linting rules
- **Prettier Config**: `.prettierrc` - Formatting rules
- **Python Project**: `src/server/pyproject.toml` - LSP server configuration, dependencies, and pytest settings
- **Python Lock**: `src/server/uv.lock` - uv package manager lock file for reproducible builds
- **Python Tests**: `src/server/pytest.ini` - Pytest configuration (test paths, markers, coverage)
- **VSIX Exclusions**: `.vscodeignore` - Packaging exclusion list
