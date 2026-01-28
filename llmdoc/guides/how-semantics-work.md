# How Semantic Highlighting Works

1. **User opens .sage file:** VS Code extension activates and checks LSP configuration in `src/extension.ts`.

2. **LSP server startup:** Extension spawns Python subprocess executing `src/server/lsp.py` with stdio transport (`extension.ts` startLSP function).

3. **Initialize handshake:** Server registers `TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL` feature with legend containing 14 token types and 6 modifiers (`lsp.py:22-34`).

4. **Document change detection:** VS Code sends `semanticTokens/full` request when document content changes (`lsp.py:35-56`).

5. **Lexical analysis:** `SemanicSever.parse()` calls `doc_to_tokens()` to tokenize document using regex patterns (`utils.py:84-186`).

6. **Semantic classification:** `classify_tokens()` iterates through tokens, applying pattern matching to identify types (`utils.py:188-372`).

7. **Token encoding:** Each token encoded as 5 integers [deltaLine, deltaOffset, length, tokenType, modifierBitmask] (`lsp.py:44-50`).

8. **Response transmission:** `SemanticTokens(data=[...])` returned to VS Code client (`lsp.py:56`).

9. **Rendering:** VS Code applies theme colors based on token types (class, function, variable, method, etc.).

**Verification:** Open a .sage file, type SageMath code (e.g., `M = Matrix([[1,2],[3,4]])`), observe semantic highlighting applied to `Matrix` (class) and `M` (variable).
