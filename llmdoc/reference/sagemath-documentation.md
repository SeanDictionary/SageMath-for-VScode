# SageMath Documentation Database

## 1. Core Summary

Comprehensive documentation database for 50+ SageMath functions and 150+ class methods, including signatures, parameters, return types, examples, and categorization. Structured as typed dictionaries for LSP features (completion, hover, signature help).

## 2. Source of Truth

- **Primary Code:** `src/server/documentation.py:28-561` - FUNCTION_DOCS and METHOD_DOCS dictionaries
- **Access Functions:** `get_function_doc()`, `get_method_doc()`, `get_all_function_names()`, `get_class_methods()` → `documentation.py:564-585`
- **Format Functions:** `format_hover_markdown()`, `format_method_hover()` → `documentation.py:588-633`
- **Usage:** `src/server/lsp.py:33-36` - Imported for completion and hover handlers
- **External:** https://doc.sagemath.org/html/en/reference/index.html - Official SageMath API docs

### Documentation Structure

**FunctionDoc TypedDict:**
```python
{
    "signature": str,      # Full function signature
    "description": str,    # One-line description
    "params": [...],       # List of ParameterDoc
    "returns": str,        # Return type description
    "examples": [...],     # Code example strings
    "category": str        # Domain category
}
```

**ParameterDoc:**
```python
{
    "name": str,
    "type": str,
    "description": str,
    "default": Optional[str]
}
```

**MethodDoc (simplified):**
```python
{
    "signature": str,
    "description": str,
    "returns": str
}
```

### Categories

Number Theory (factor, is_prime, gcd, lcm, xgcd, euler_phi, divisors), Cryptography (crt, inverse_mod, power_mod, discrete_log, random_prime), Linear Algebra (matrix, vector, identity_matrix, zero_matrix, diagonal_matrix, block_matrix, random_matrix), Algebra (PolynomialRing, GF, Zmod, Mod, Ideal), Symbolic (var, solve, expand, simplify), Calculus (diff, integrate, limit, taylor), Elliptic Curves (EllipticCurve), Utilities (sqrt, log, exp, abs, floor, ceil, show, latex, plot).
