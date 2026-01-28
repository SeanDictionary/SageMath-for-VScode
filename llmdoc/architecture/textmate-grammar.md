# TextMate Grammar Architecture

## 1. Identity

- **What it is:** A minimal TextMate grammar definition that extends Python's grammar for SageMath files.
- **Purpose:** Provides basic syntax highlighting by inheriting Python's grammar and adding SageMath-specific comment patterns.

## 2. Core Components

- `syntaxes/sagemath.tmLanguage.json` (scopeName, patterns, repository): Grammar definition file that declares `source.sagemath` scope and defines custom comment patterns.
- `language-configuration.json` (comments, brackets, autoClosingPairs): VS Code language behavior configuration for editor features.
- `package.json` (languages, grammars): Registers the SageMath language and maps it to the grammar file.

## 3. Execution Flow (LLM Retrieval Map)

- **1. File Detection:** VS Code detects `.sage` extension via `package.json:45` or first-line match (`# Sage`, `from Sage`) in `sagemath.tmLanguage.json:6`.
- **2. Scope Assignment:** Language assigned `source.sagemath` scope via `sagemath.tmLanguage.json:4`.
- **3. Pattern Matching:** Grammar applies comment patterns from `sagemath.tmLanguage.json:16-54`, then includes Python grammar via `"include": "source.python"` at line 12.
- **4. Tokenization:** TextMate tokenizer produces scopes for theming (e.g., `comment.line.number-sign.sagemath`, `string.quoted.docstring.multi.sagemath`).

## 4. Design Rationale

The grammar follows a minimal design pattern: rather than duplicating Python's complex syntax rules, it inherits them via `"include": "source.python"` and only defines SageMath-specific comment handling. This ensures compatibility with Python themes and reduces maintenance burden.
