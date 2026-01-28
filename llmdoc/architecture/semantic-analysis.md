# Semantic Analysis Architecture

## 1. Identity

- **What it is:** Single-pass token classification algorithm using pattern matching on sequential context.
- **Purpose:** Identifies and classifies symbols as functions, classes, methods, variables, properties, and constants for semantic highlighting and completion.

## 2. Core Components

- `src/server/utils.py:188-372` (SemanicSever.classify_tokens): Classification engine implementing recognition patterns.
- `src/server/symbols.py:86-182` (SymbolExtractor.extract_symbols): Alternative symbol extraction for outline, navigation, and type inference.
- `src/server/predefinition.py:17-93` (FUNCTIONS): Set of 150+ predefined SageMath function names.
- `src/server/predefinition.py:96-192` (CLASSES): Dictionary of 30+ classes with methods and properties.
- `src/server/predefinition.py:6-11` (KEYWORDS): Python keyword set for pattern matching.

## 3. Execution Flow (LLM Retrieval Map)

- **1. Data Structure Initialization:** Creates shallow copies of standard library definitions and empty tracking sets (`utils.py:191-194`).
- **2. Sequential Token Iteration:** Processes tokens in order, maintaining context from previous tokens (`utils.py:196`).
- **3. Pattern Matching (Priority Order):**
  - **Keyword recognition:** `class`, `def`, `from`, `import`, `for` trigger context-specific classification (`utils.py:201-279`)
  - **Polynomial ring variables:** `R.<x> =` pattern for SageMath polynomial rings (`utils.py:295-315`)
  - **Standard library lookup:** Token text matched against `function_names`, `class_names`, `variable_names` sets (`utils.py:320-340`)
- **4. Dynamic Symbol Registration:**
  - Class definitions add to `class_names` (`utils.py:203-205`)
  - Function definitions add to `function_names` (`utils.py:236-244`)
  - Variable assignments add to `variable_names` (`utils.py:343-365`)
- **5. Member Resolution:** For `a.b` patterns, resolves `b` against known methods/properties of `a`'s type (`utils.py:330-336`).

**Recognition patterns:** Class definition (`class X:`), method definition (`def m(self):`), import statements (`from X import Y`, `import X`), loop variables (`for x in`), polynomial ring syntax (`R.<x> =`), assignment (`a = b`), member access (`a.b`).

## 4. Design Rationale

Single-pass classification trades accuracy for performance (O(n) vs. O(n²) for full type inference). Shallow copies of standard library definitions reduce memory overhead while preventing mutation of original definitions. Pattern matching on sequential context enables recognition without AST construction. Limitations: No cross-file analysis, no chained call support (`a.b.c()`), limited type inference.

**Scope:** Single-file analysis only; no inter-module symbol resolution.
