# SageMath Token Types Reference

## 1. Core Summary

SageMath LSP defines 14 token types and 6 token modifiers following the LSP specification. Tokens are encoded as 5 integers per token using delta encoding for efficient transmission.

## 2. Source of Truth

- **Primary Code:** `src/server/predefinition.py:1-3` - Token type and modifier definitions
- **Encoding Logic:** `src/server/lsp.py:9-10,44-50` - Token to integer encoding/decoding
- **Usage:** `src/server/utils.py:188-373` - Semantic classification assigns types to tokens

### Token Types (14)

| Index | Type | Description | Example Usage |
|-------|------|-------------|---------------|
| 0 | namespace | Module/package imports | `from sage.all import Matrix` |
| 1 | type | Type annotations | `: int`, `: str` |
| 2 | class | Class definitions | `class MyClass:` |
| 3 | function | Function definitions/calls | `def foo():`, `gcd(a, b)` |
| 4 | variable | Variable assignments | `x = 10` |
| 5 | parameter | Function parameters | `def foo(param):` |
| 6 | property | Class properties | `self.prop` |
| 7 | method | Class methods | `def myMethod(self):` |
| 8 | keyword | Python/SageMath keywords | `if`, `for`, `def` |
| 9 | modifier | Type modifiers | `async`, `await` |
| 10 | operator | Arithmetic/logical operators | `+`, `*`, `==` |
| 11 | string | String literals | `"text"` |
| 12 | number | Numeric literals | `42`, `3.14` |
| 13 | comment | Comments | `# comment` |

### Token Modifiers (6)

| Bit | Modifier | Description |
|-----|----------|-------------|
| 0 | declaration | Token is a declaration |
| 1 | definition | Token is a definition |
| 2 | readonly | Read-only variable |
| 3 | static | Static member |
| 4 | deprecated | Deprecated usage |
| 5 | defaultLibrary | From standard library |

### Encoding Format

Each token encoded as `[deltaLine, deltaOffset, length, tokenType, modifierBitmask]`:

- **deltaLine**: Line difference from previous token
- **deltaOffset**: Character difference from previous token
- **length**: Token text length
- **tokenType**: Index into TOKEN_TYPES array
- **modifierBitmask**: Bitwise OR of modifier indices (2^index)
