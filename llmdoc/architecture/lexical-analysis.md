# Lexical Analysis Architecture

## 1. Identity

- **What it is:** Line-by-line tokenization algorithm using pre-compiled regex patterns.
- **Purpose:** Converts raw SageMath source code into a stream of Token objects with position tracking.

## 2. Core Components

- `src/server/utils.py:48-56` (SYMBOL, NUMBER, OP, SPACE, COMMENT, BLOCK_STRING_BEGIN/END, LINE_STRING, MATCH_ALL_LINE): Module-level compiled regex patterns for token matching.
- `src/server/utils.py:84-186` (SemanicSever.doc_to_tokens): Tokenization engine implementing priority-based pattern matching.
- `src/server/utils.py:59-71` (Token): Data class storing line delta, offset delta, text, type, and modifiers.

## 3. Execution Flow (LLM Retrieval Map)

- **1. Pattern Compilation:** Regex patterns compiled at module load time in `utils.py:48-56`.
- **2. Document Iteration:** `doc_to_tokens()` receives TextDocument, iterates through each line (`utils.py:112-184`).
- **3. Pattern Matching:** For each line, applies patterns in priority order (SPACE → COMMENT → SYMBOL → OP → NUMBER → STRING) (`utils.py:118-170`).
- **4. Token Creation:** When SYMBOL or OP matches, `add_token()` creates Token with delta encoding (`utils.py:92-108`).
- **5. Position Tracking:** Maintains `prev_line`, `prev_offset`, `current_line`, `current_offset` for delta calculation (`utils.py:88-108`).
- **6. Error Handling:** Logs unmatched characters and detects infinite loops via `chars_left` comparison (`utils.py:172-182`).

**Tokenization policy:** Only SYMBOL (identifiers) and OP (operators) are extracted; comments, strings, and numbers are skipped for native Python syntax highlighting.

## 4. Design Rationale

Delta encoding (storing relative positions from previous token) minimizes data transmission size over LSP protocol. Module-level regex compilation avoids recompilation overhead on each request. Priority-based pattern matching ensures correct token disambiguation (e.g., operators before symbols).
