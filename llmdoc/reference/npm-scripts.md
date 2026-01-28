# NPM Scripts Reference

## 1. Core Summary

Available npm scripts defined in `package.json`. These are the primary commands for development, testing, and packaging.

## 2. Source of Truth

- **Primary Code**: `package.json:159-170` - Script definitions
- **Related Guide**: `/llmdoc/guides/how-to-build-and-package.md` - Build workflow

## Available Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `compile` | `tsc -p ./` | One-time TypeScript compilation |
| `watch` | `tsc -watch -p ./` | Incremental compilation with file watching |
| `lint` | `eslint src --ext ts` | Check TypeScript code quality |
| `lint:fix` | `eslint src --ext ts --fix` | Auto-fix linting issues |
| `format` | `prettier --write "src/**/*.ts"` | Format code with Prettier |
| `format:check` | `prettier --check "src/**/*.ts"` | Verify code formatting |
| `pretest` | `npm run compile` | Pre-test compilation hook |
| `test` | `node ./out/test/runTest.js` | Run integration tests |
| `package` | `vsce package` | Create `.vsix` extension package |
| `publish` | `vsce publish` | Publish to marketplace |

## Dependencies

- **TypeScript Config**: `tsconfig.json` - Compiler options
- **ESLint Config**: `.eslintrc.json` - Linting rules
- **Prettier Config**: `.prettierrc` - Formatting rules
- **VSIX Exclusions**: `.vscodeignore` - Packaging exclusion list
