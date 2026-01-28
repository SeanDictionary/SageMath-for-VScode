# Semantic Token System Architecture

## 1. Identity

- **What it is:** A custom LSP server that performs lexical and semantic analysis to provide enhanced syntax highlighting for SageMath.
- **Purpose:** Classifies tokens beyond basic syntax (functions, classes, methods, variables) with knowledge of SageMath's standard library.

## 2. Core Components

- `src/extension.ts` (startLSP, client): Starts LSP server using Python virtual environment, configures stdio transport, handles document selector for `sagemath` language.
- `src/server/lsp.py` (semantic_tokens, initialize): LSP protocol handlers, converts tokens to 5-integer encoding format, configures token legend.
- `src/server/utils.py` (SemanicSever, doc_to_tokens, classify_tokens): Implements lexical analysis via regex patterns and semantic classification tracking user-defined symbols.
- `src/server/predefinition.py` (TOKEN_TYPES, TOKEN_MODIFIERS, FUNCTIONS, CLASSES): Defines LSP token type legend and SageMath standard library (93 functions, 45 classes).

## 3. Execution Flow (LLM Retrieval Map)

- **1. Server Startup:** `extension.ts:202-241` starts Python process from `src/server/envLSP/`, passes `src/server/lsp.py` as server module.
- **2. Initialize Handler:** `lsp.py:26-30` receives `initialize` request, configures logging.
- **3. Token Request:** `lsp.py:34-56` receives `textDocument/semanticTokens/full` request, calls `ls.parse()`.
- **4. Lexical Analysis:** `utils.py:84-173` runs `doc_to_tokens()` using regex patterns (SYMBOL, NUMBER, OP, COMMENT) to extract identifiers.
- **5. Semantic Classification:** `utils.py:188-373` runs `classify_tokens()` matching patterns like `class`, `def`, `R.<x> =`, `for ... in` to determine token types.
- **6. Library Lookup:** `utils.py:188-193` checks if identifiers match `predefinition.py:17-93` (FUNCTIONS) or `predefinition.py:96-192` (CLASSES).
- **7. Token Encoding:** `lsp.py:44-50` encodes each token as 5 integers: [deltaLine, deltaOffset, length, tokenType, tokenModifiers].
- **8. Response:** Returns `SemanticTokens` data array to VS Code for rendering.

## 4. Design Rationale

The system uses a two-phase analysis approach: lexical analysis extracts all symbols via regex, then semantic classification interprets their meaning based on context (preceding keywords, surrounding patterns). This separation allows for easier extension of new patterns without modifying the core tokenization logic. The predefined library provides instant recognition of SageMath's mathematical constructs without requiring external type information.
