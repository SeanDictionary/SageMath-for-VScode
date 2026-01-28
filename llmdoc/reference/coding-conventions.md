# Coding Conventions

## 1. Core Summary

This project uses TypeScript with strict ESLint and Prettier configurations. Code should follow ESLint recommended rules, use TypeScript strict mode, and adhere to the formatting standards defined below.

## 2. Source of Truth

- **ESLint Config:** `/.eslintrc.json` - Primary linting rules and TypeScript standards
- **Prettier Config:** `/.prettierrc` - Code formatting rules
- **Editor Config:** `/.editorconfig` - Editor settings for consistent encoding and indentation
- **TypeScript Config:** `/tsconfig.json` - Compiler options and type checking settings
- **Lint Scripts:** `/package.json:164-167` - NPM scripts for linting and formatting

### Key ESLint Rules (`/.eslintrc.json:16-37`)
- Variables: `camelCase`, `UPPER_CASE`, or `PascalCase` with optional leading underscore
- Semicolons: Required (always)
- Unused variables: Warning only; prefix with `_` to ignore
- `any` types: Warning (avoid when possible)
- Braces: Required for all control structures
- Equality: Strict equality (`===`) required
- No `var` keywords; use `const`/`let`

### Prettier Formatting (`/.prettierrc`)
- Indent: 4 spaces (2 for JSON/YAML)
- Quotes: Single quotes
- Semicolons: Enabled
- Line width: 120 characters
- Trailing commas: None
- Arrow function parentheses: Omit when possible
- Line endings: LF

### TypeScript Compiler (`/tsconfig.json:2-17`)
- Target: ES2022
- Module: Node16
- Strict mode: Enabled
- Source maps: Enabled
- Declarations: Generated
- Root directory: `/src`
