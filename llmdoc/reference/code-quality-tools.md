# Code Quality Tools Reference

## 1. Core Summary

Code quality enforcement using ESLint, Prettier, and EditorConfig for consistent TypeScript formatting and linting standards across the project.

## 2. Source of Truth

- **ESLint Config**: `.eslintrc.json` - TypeScript linting rules with @typescript-eslint plugin
- **Prettier Config**: `.prettierrc` - Code formatting rules
- **EditorConfig**: `.editorconfig` - Editor-agnostic formatting settings
- **Related Scripts**: `package.json:159-170` - `lint`, `lint:fix`, `format`, `format:check` commands

## ESLint (`.eslintrc.json`)

**Parser**: @typescript-eslint/parser with project-based type checking

**Rules**:
- TypeScript naming conventions (camelCase, UPPER_CASE, PascalCase)
- Semi-colons required
- No unused variables (warn, with `_` prefix ignore)
- No explicit `any` (warn)
- Strict equality checks (`===`)
- No `var` declarations

**Ignore Patterns**: `out`, `dist`, `**/*.d.ts`, `node_modules`

## Prettier (`.prettierrc`)

**Settings**:
- Semi-colons: `true`
- Quotes: Single
- Tab width: `4`
- Tabs: `false` (use spaces)
- Trailing commas: `none`
- Print width: `120`
- End of line: `lf`

## EditorConfig (`.editorconfig`)

Applies consistent formatting across different editors and IDEs. Refer to `.editorconfig` for charset, indent style, and trailing whitespace rules.
