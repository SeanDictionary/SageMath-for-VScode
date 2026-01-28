# SageMath Standard Library Reference

## 1. Core Summary

The LSP server maintains predefined definitions for 150+ SageMath functions and 45 classes with methods and properties. These definitions enable semantic highlighting, code completion, and documentation lookup. Enhanced by comprehensive documentation database in `documentation.py` with signatures, parameters, examples.

## 2. Source of Truth

- **Primary Code:** `src/server/predefinition.py:1-193` - Complete function and class definitions
- **Documentation:** `src/server/documentation.py:28-561` - Detailed function/method documentation with signatures and examples
- **Usage:** `src/server/utils.py:188-193` - Library lookup during token classification
- **Usage:** `src/server/lsp.py:328-433` - Completion and hover handlers
- **External Reference:** https://doc.sagemath.org/html/en/reference/index.html - Official SageMath documentation

### Predefined Functions (93)

Organized by domain:

**Basic Arithmetic:** `GCD`, `gcd`, `LCM`, `lcm`, `xgcd`, `crt`, `factor`, `prime_factors`, `divisors`, `is_prime`, `factorial`, `binomial`, `fibonacci`

**Number Theory:** `euler_phi`, `moebius`, `sigma`, `kronecker_symbol`, `legendre_symbol`, `jacobi_symbol`, `power_mod`, `inverse_mod`, `mod`, `Mod`

**Algebra:** `expand`, `simplify`, `collect`, `trigsimp`, `powsimp`

**Calculus:** `diff`, `derivative`, `integrate`, `integral`, `limit`, `taylor`, `series`, `laplace`, `inverse_laplace`

**Solving:** `solve`, `solve_mod`, `roots`, `find_root`

**Linear Algebra:** `Matrix`, `matrix`, `vector`, `identity_matrix`, `zero_matrix`, `diagonal_matrix`, `block_matrix`, `random_matrix`

**Polynomials:** `poly`, `degree`, `coefficients`, `resultant`, `discriminant`

**Combinatorics:** `permutations`, `combinations`, `partitions`, `bell_number`, `bernoulli`, `stirling_number1`

**Graph Theory:** `Graph`, `DiGraph`, `graphs`, `digraphs`

**Elliptic Curves:** `EllipticCurve`, `EllipticCurve_from_j`

**Plotting:** `plot`, `list_plot`, `scatter_plot`, `parametric_plot`, `plot3d`

**Symbolic:** `var`, `assume`, `SR`, `Expression`

**Utilities:** `show`, `latex`, `randint`, `abs`, `sqrt`, `sin`, `cos`, `pi`, `e`, `I`, `oo`

### Predefined Classes (45)

Each class includes methods and properties for member highlighting:

**Base Rings:** `ZZ`, `QQ`, `RR`, `CC`, `RDF`, `CDF`, `RIF`, `CIF`

**Modular Arithmetic:** `Zmod`, `IntegerModRing`, `GF`, `FiniteField`

**Polynomials:** `PolynomialRing`, `Polynomial`, `Ideal`

**Matrices:** `Matrix`, `vector`, `FreeModule`

**Symbolic:** `var`, `SR`, `Expression`

**Number Fields:** `NumberField`, `QuadraticField`, `CyclotomicField`, `FunctionField`

**Elliptic Curves:** `EllipticCurve`

**Groups:** `AbelianGroup`, `PermutationGroup`, `SymmetricGroup`, `DihedralGroup`

**Graphs:** `Graph`, `DiGraph`

**Power Series:** `PowerSeriesRing`, `LaurentSeriesRing`

**Integers/Rationals:** `Integer`, `Rational`

**Sequences:** `Sequence`, `OEIS`

### Keyword Set (32)

`for`, `if`, `else`, `elif`, `while`, `return`, `import`, `from`, `as`, `try`, `except`, `finally`, `with`, `yield`, `def`, `class`, `lambda`, `assert`, `break`, `continue`, `pass`, `global`, `nonlocal`, `del`, `raise`, `in`, `is`, `not`, `and`, `or`, `True`, `False`, `None`, `self`, `async`, `await`
