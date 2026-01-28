"""
SageMath Documentation Database for LSP Features
Contains function signatures, descriptions, parameters, examples
"""

from __future__ import annotations
from typing import TypedDict, Optional


class ParameterDoc(TypedDict):
    name: str
    type: str
    description: str
    default: Optional[str]


class FunctionDoc(TypedDict):
    signature: str
    description: str
    params: list[ParameterDoc]
    returns: str
    examples: list[str]
    category: str


# ============== Function Documentation ==============

FUNCTION_DOCS: dict[str, FunctionDoc] = {
    # ==================== Number Theory ====================
    "factor": {
        "signature": "factor(n, proof=None, int_=False, algorithm='pari', verbose=0)",
        "description": "Return the factorization of n. The result depends on the type of n.",
        "params": [
            {"name": "n", "type": "integer/polynomial", "description": "The object to factor", "default": None},
            {"name": "proof", "type": "bool", "description": "Whether to prove primality of factors", "default": "None"},
            {"name": "algorithm", "type": "str", "description": "Algorithm: 'pari', 'kash', 'magma'", "default": "'pari'"},
        ],
        "returns": "Factorization object",
        "examples": ["factor(120)  # 2^3 * 3 * 5", "factor(x^4 - 1)"],
        "category": "number_theory",
    },
    "is_prime": {
        "signature": "is_prime(n, proof=None)",
        "description": "Return True if n is a prime number, False otherwise.",
        "params": [
            {"name": "n", "type": "integer", "description": "Number to test", "default": None},
            {"name": "proof", "type": "bool", "description": "Use provable test", "default": "None"},
        ],
        "returns": "bool",
        "examples": ["is_prime(17)  # True", "is_prime(15)  # False"],
        "category": "number_theory",
    },
    "next_prime": {
        "signature": "next_prime(n, proof=None)",
        "description": "Return the smallest prime greater than n.",
        "params": [{"name": "n", "type": "integer", "description": "Starting number", "default": None}],
        "returns": "integer",
        "examples": ["next_prime(10)  # 11"],
        "category": "number_theory",
    },
    "gcd": {
        "signature": "gcd(a, b=None)",
        "description": "Return the greatest common divisor of a and b.",
        "params": [
            {"name": "a", "type": "integer/list", "description": "First number or list", "default": None},
            {"name": "b", "type": "integer", "description": "Second number", "default": "None"},
        ],
        "returns": "integer",
        "examples": ["gcd(12, 18)  # 6", "gcd([12, 18, 24])  # 6"],
        "category": "number_theory",
    },
    "lcm": {
        "signature": "lcm(a, b=None)",
        "description": "Return the least common multiple of a and b.",
        "params": [
            {"name": "a", "type": "integer/list", "description": "First number or list", "default": None},
            {"name": "b", "type": "integer", "description": "Second number", "default": "None"},
        ],
        "returns": "integer",
        "examples": ["lcm(12, 18)  # 36"],
        "category": "number_theory",
    },
    "xgcd": {
        "signature": "xgcd(a, b)",
        "description": "Extended GCD: return (g, s, t) such that g = gcd(a,b) = s*a + t*b.",
        "params": [
            {"name": "a", "type": "integer", "description": "First number", "default": None},
            {"name": "b", "type": "integer", "description": "Second number", "default": None},
        ],
        "returns": "tuple (g, s, t)",
        "examples": ["xgcd(12, 8)  # (4, 1, -1)"],
        "category": "number_theory",
    },
    "euler_phi": {
        "signature": "euler_phi(n)",
        "description": "Return Euler's totient function φ(n).",
        "params": [{"name": "n", "type": "integer", "description": "Positive integer", "default": None}],
        "returns": "integer",
        "examples": ["euler_phi(12)  # 4"],
        "category": "number_theory",
    },
    "divisors": {
        "signature": "divisors(n)",
        "description": "Return all positive divisors of n.",
        "params": [{"name": "n", "type": "integer", "description": "Positive integer", "default": None}],
        "returns": "list",
        "examples": ["divisors(12)  # [1, 2, 3, 4, 6, 12]"],
        "category": "number_theory",
    },
    "factorial": {
        "signature": "factorial(n, algorithm='gmp')",
        "description": "Return n! = 1 * 2 * ... * n.",
        "params": [{"name": "n", "type": "integer", "description": "Non-negative integer", "default": None}],
        "returns": "integer",
        "examples": ["factorial(5)  # 120"],
        "category": "number_theory",
    },
    "binomial": {
        "signature": "binomial(n, k)",
        "description": "Return binomial coefficient C(n,k).",
        "params": [
            {"name": "n", "type": "integer", "description": "Total items", "default": None},
            {"name": "k", "type": "integer", "description": "Items to choose", "default": None},
        ],
        "returns": "integer",
        "examples": ["binomial(5, 2)  # 10"],
        "category": "number_theory",
    },
    
    # ==================== Cryptography ====================
    "crt": {
        "signature": "crt(remainders, moduli)",
        "description": "Chinese Remainder Theorem: find x ≡ remainders[i] (mod moduli[i]).",
        "params": [
            {"name": "remainders", "type": "list", "description": "List of remainders", "default": None},
            {"name": "moduli", "type": "list", "description": "List of moduli (pairwise coprime)", "default": None},
        ],
        "returns": "integer",
        "examples": ["crt([2, 3, 2], [3, 5, 7])  # 23"],
        "category": "cryptography",
    },
    "inverse_mod": {
        "signature": "inverse_mod(a, m)",
        "description": "Return b such that a*b ≡ 1 (mod m).",
        "params": [
            {"name": "a", "type": "integer", "description": "Number to invert", "default": None},
            {"name": "m", "type": "integer", "description": "Modulus", "default": None},
        ],
        "returns": "integer",
        "examples": ["inverse_mod(3, 7)  # 5"],
        "category": "cryptography",
    },
    "power_mod": {
        "signature": "power_mod(a, n, m)",
        "description": "Return a^n mod m using fast exponentiation.",
        "params": [
            {"name": "a", "type": "integer", "description": "Base", "default": None},
            {"name": "n", "type": "integer", "description": "Exponent", "default": None},
            {"name": "m", "type": "integer", "description": "Modulus", "default": None},
        ],
        "returns": "integer",
        "examples": ["power_mod(2, 10, 1000)  # 24"],
        "category": "cryptography",
    },
    "discrete_log": {
        "signature": "discrete_log(a, base, ord=None, operation='*')",
        "description": "Compute discrete log: find x such that base^x = a.",
        "params": [
            {"name": "a", "type": "element", "description": "Target element", "default": None},
            {"name": "base", "type": "element", "description": "Base", "default": None},
            {"name": "ord", "type": "integer", "description": "Order of base", "default": "None"},
        ],
        "returns": "integer",
        "examples": ["F = GF(101); discrete_log(F(2), F(3))"],
        "category": "cryptography",
    },
    "random_prime": {
        "signature": "random_prime(n, proof=None, lbound=2)",
        "description": "Return a random prime p with lbound <= p <= n.",
        "params": [
            {"name": "n", "type": "integer", "description": "Upper bound", "default": None},
            {"name": "lbound", "type": "integer", "description": "Lower bound", "default": "2"},
        ],
        "returns": "integer",
        "examples": ["random_prime(2^256, lbound=2^255)"],
        "category": "cryptography",
    },
    
    # ==================== Linear Algebra ====================
    "matrix": {
        "signature": "matrix(ring, nrows, ncols=None, entries=None, sparse=False)",
        "description": "Create a matrix over the given ring.",
        "params": [
            {"name": "ring", "type": "Ring", "description": "Base ring (ZZ, QQ, GF(p))", "default": None},
            {"name": "nrows", "type": "integer", "description": "Number of rows", "default": None},
            {"name": "ncols", "type": "integer", "description": "Number of columns", "default": "None"},
            {"name": "entries", "type": "list", "description": "Matrix entries", "default": "None"},
        ],
        "returns": "Matrix",
        "examples": ["matrix(ZZ, 2, 2, [1,2,3,4])", "matrix(QQ, [[1,2],[3,4]])"],
        "category": "linear_algebra",
    },
    "vector": {
        "signature": "vector(ring, entries)",
        "description": "Create a vector over the given ring.",
        "params": [
            {"name": "ring", "type": "Ring", "description": "Base ring", "default": None},
            {"name": "entries", "type": "list", "description": "Vector entries", "default": None},
        ],
        "returns": "Vector",
        "examples": ["vector(ZZ, [1, 2, 3])"],
        "category": "linear_algebra",
    },
    "identity_matrix": {
        "signature": "identity_matrix(ring, n, sparse=False)",
        "description": "Return n x n identity matrix.",
        "params": [
            {"name": "ring", "type": "Ring", "description": "Base ring", "default": None},
            {"name": "n", "type": "integer", "description": "Dimension", "default": None},
        ],
        "returns": "Matrix",
        "examples": ["identity_matrix(ZZ, 3)"],
        "category": "linear_algebra",
    },
    "zero_matrix": {
        "signature": "zero_matrix(ring, nrows, ncols=None)",
        "description": "Return zero matrix.",
        "params": [
            {"name": "ring", "type": "Ring", "description": "Base ring", "default": None},
            {"name": "nrows", "type": "integer", "description": "Rows", "default": None},
            {"name": "ncols", "type": "integer", "description": "Columns", "default": "None"},
        ],
        "returns": "Matrix",
        "examples": ["zero_matrix(ZZ, 3, 4)"],
        "category": "linear_algebra",
    },
    "diagonal_matrix": {
        "signature": "diagonal_matrix(ring, entries)",
        "description": "Return diagonal matrix with given entries.",
        "params": [
            {"name": "ring", "type": "Ring", "description": "Base ring", "default": None},
            {"name": "entries", "type": "list", "description": "Diagonal entries", "default": None},
        ],
        "returns": "Matrix",
        "examples": ["diagonal_matrix(ZZ, [1, 2, 3])"],
        "category": "linear_algebra",
    },
    "block_matrix": {
        "signature": "block_matrix(ring, blocks, subdivide=True)",
        "description": "Create block matrix from sub-matrices.",
        "params": [
            {"name": "blocks", "type": "list", "description": "List of sub-matrices", "default": None},
        ],
        "returns": "Matrix",
        "examples": ["block_matrix([[A, B], [C, D]])"],
        "category": "linear_algebra",
    },
    "random_matrix": {
        "signature": "random_matrix(ring, nrows, ncols=None)",
        "description": "Return random matrix.",
        "params": [
            {"name": "ring", "type": "Ring", "description": "Base ring", "default": None},
            {"name": "nrows", "type": "integer", "description": "Rows", "default": None},
        ],
        "returns": "Matrix",
        "examples": ["random_matrix(ZZ, 3, 3)"],
        "category": "linear_algebra",
    },
    
    # ==================== Algebra ====================
    "PolynomialRing": {
        "signature": "PolynomialRing(base_ring, names, order='degrevlex')",
        "description": "Create polynomial ring over base_ring.",
        "params": [
            {"name": "base_ring", "type": "Ring", "description": "Coefficient ring", "default": None},
            {"name": "names", "type": "str/list", "description": "Variable names", "default": None},
        ],
        "returns": "PolynomialRing",
        "examples": ["R.<x> = PolynomialRing(QQ)", "R.<x,y> = PolynomialRing(ZZ)"],
        "category": "algebra",
    },
    "GF": {
        "signature": "GF(order, name='a', modulus=None)",
        "description": "Create finite field of given order (prime power).",
        "params": [
            {"name": "order", "type": "integer", "description": "Field order p^n", "default": None},
            {"name": "name", "type": "str", "description": "Generator name", "default": "'a'"},
        ],
        "returns": "FiniteField",
        "examples": ["GF(7)", "GF(2^8)", "K.<a> = GF(2^8)"],
        "category": "algebra",
    },
    "Zmod": {
        "signature": "Zmod(n)",
        "description": "Create ring of integers modulo n.",
        "params": [{"name": "n", "type": "integer", "description": "Modulus", "default": None}],
        "returns": "IntegerModRing",
        "examples": ["R = Zmod(12); R(7) + R(8)"],
        "category": "algebra",
    },
    "Mod": {
        "signature": "Mod(n, m)",
        "description": "Return n mod m as element of Z/mZ.",
        "params": [
            {"name": "n", "type": "integer", "description": "Number", "default": None},
            {"name": "m", "type": "integer", "description": "Modulus", "default": None},
        ],
        "returns": "IntegerMod",
        "examples": ["Mod(17, 5)  # 2"],
        "category": "algebra",
    },
    "Ideal": {
        "signature": "Ideal(ring, gens)",
        "description": "Create ideal generated by given elements.",
        "params": [
            {"name": "ring", "type": "Ring", "description": "Parent ring", "default": None},
            {"name": "gens", "type": "list", "description": "Generators", "default": None},
        ],
        "returns": "Ideal",
        "examples": ["R.<x,y> = QQ[]; I = Ideal([x^2, y^2])"],
        "category": "algebra",
    },
    
    # ==================== Symbolic ====================
    "var": {
        "signature": "var(names)",
        "description": "Create symbolic variables.",
        "params": [{"name": "names", "type": "str", "description": "Variable names", "default": None}],
        "returns": "Symbolic variable(s)",
        "examples": ["var('x')", "var('x y z')"],
        "category": "symbolic",
    },
    "solve": {
        "signature": "solve(f, *args, **kwds)",
        "description": "Solve equations algebraically.",
        "params": [
            {"name": "f", "type": "equation/list", "description": "Equation(s)", "default": None},
            {"name": "args", "type": "variables", "description": "Variables to solve for", "default": None},
        ],
        "returns": "list of solutions",
        "examples": ["var('x'); solve(x^2 - 4 == 0, x)"],
        "category": "symbolic",
    },
    "expand": {
        "signature": "expand(expr)",
        "description": "Expand expression by distributing products.",
        "params": [{"name": "expr", "type": "Expression", "description": "Expression", "default": None}],
        "returns": "Expression",
        "examples": ["var('x'); expand((x+1)^3)"],
        "category": "symbolic",
    },
    "simplify": {
        "signature": "simplify(expr)",
        "description": "Simplify a symbolic expression.",
        "params": [{"name": "expr", "type": "Expression", "description": "Expression", "default": None}],
        "returns": "Expression",
        "examples": ["simplify(sin(x)^2 + cos(x)^2)  # 1"],
        "category": "symbolic",
    },
    
    # ==================== Calculus ====================
    "diff": {
        "signature": "diff(f, *args)",
        "description": "Compute derivative.",
        "params": [
            {"name": "f", "type": "Expression", "description": "Function", "default": None},
            {"name": "args", "type": "variables", "description": "Differentiate w.r.t.", "default": None},
        ],
        "returns": "Expression",
        "examples": ["var('x'); diff(x^3, x)  # 3*x^2"],
        "category": "calculus",
    },
    "integrate": {
        "signature": "integrate(f, *args)",
        "description": "Compute integral.",
        "params": [
            {"name": "f", "type": "Expression", "description": "Function", "default": None},
            {"name": "args", "type": "variable/bounds", "description": "Variable and bounds", "default": None},
        ],
        "returns": "Expression",
        "examples": ["var('x'); integrate(x^2, x)  # x^3/3"],
        "category": "calculus",
    },
    "limit": {
        "signature": "limit(f, x=a, dir=None)",
        "description": "Compute limit as x approaches a.",
        "params": [
            {"name": "f", "type": "Expression", "description": "Function", "default": None},
            {"name": "dir", "type": "str", "description": "Direction: '+', '-'", "default": "None"},
        ],
        "returns": "Expression",
        "examples": ["var('x'); limit(sin(x)/x, x=0)  # 1"],
        "category": "calculus",
    },
    "taylor": {
        "signature": "taylor(f, x, a, n)",
        "description": "Taylor series around x=a to order n.",
        "params": [
            {"name": "f", "type": "Expression", "description": "Function", "default": None},
            {"name": "x", "type": "variable", "description": "Variable", "default": None},
            {"name": "a", "type": "value", "description": "Expansion point", "default": None},
            {"name": "n", "type": "integer", "description": "Order", "default": None},
        ],
        "returns": "Expression",
        "examples": ["var('x'); taylor(exp(x), x, 0, 5)"],
        "category": "calculus",
    },
    
    # ==================== Elliptic Curves ====================
    "EllipticCurve": {
        "signature": "EllipticCurve(field, ainvs)",
        "description": "Create elliptic curve. Essential for CTF crypto.",
        "params": [
            {"name": "field", "type": "Ring/list", "description": "Base field or coefficients", "default": None},
            {"name": "ainvs", "type": "list", "description": "Weierstrass coefficients", "default": None},
        ],
        "returns": "EllipticCurve",
        "examples": ["EllipticCurve(GF(101), [0, 7])", "E = EllipticCurve(QQ, [0,0,0,-1,0])"],
        "category": "elliptic_curves",
    },
    
    # ==================== Utilities ====================
    "sqrt": {
        "signature": "sqrt(x)",
        "description": "Return square root of x.",
        "params": [{"name": "x", "type": "number", "description": "Value", "default": None}],
        "returns": "number/Expression",
        "examples": ["sqrt(4)  # 2", "sqrt(2).n()  # 1.414..."],
        "category": "utility",
    },
    "log": {
        "signature": "log(x, base=None)",
        "description": "Return logarithm (default: natural log).",
        "params": [
            {"name": "x", "type": "number", "description": "Value", "default": None},
            {"name": "base", "type": "number", "description": "Base", "default": "None"},
        ],
        "returns": "number/Expression",
        "examples": ["log(e)  # 1", "log(100, 10)  # 2"],
        "category": "utility",
    },
    "exp": {
        "signature": "exp(x)",
        "description": "Return e^x.",
        "params": [{"name": "x", "type": "number", "description": "Exponent", "default": None}],
        "returns": "number/Expression",
        "examples": ["exp(1)  # e"],
        "category": "utility",
    },
    "abs": {
        "signature": "abs(x)",
        "description": "Return absolute value.",
        "params": [{"name": "x", "type": "number", "description": "Value", "default": None}],
        "returns": "number",
        "examples": ["abs(-5)  # 5"],
        "category": "utility",
    },
    "floor": {
        "signature": "floor(x)",
        "description": "Return floor (largest integer <= x).",
        "params": [{"name": "x", "type": "number", "description": "Value", "default": None}],
        "returns": "integer",
        "examples": ["floor(3.7)  # 3"],
        "category": "utility",
    },
    "ceil": {
        "signature": "ceil(x)",
        "description": "Return ceiling (smallest integer >= x).",
        "params": [{"name": "x", "type": "number", "description": "Value", "default": None}],
        "returns": "integer",
        "examples": ["ceil(3.2)  # 4"],
        "category": "utility",
    },
    "show": {
        "signature": "show(object)",
        "description": "Display object (graphics, matrix, etc.).",
        "params": [{"name": "object", "type": "any", "description": "Object to display", "default": None}],
        "returns": "None",
        "examples": ["show(matrix([[1,2],[3,4]]))"],
        "category": "utility",
    },
    "latex": {
        "signature": "latex(object)",
        "description": "Return LaTeX representation.",
        "params": [{"name": "object", "type": "any", "description": "Object", "default": None}],
        "returns": "str",
        "examples": ["latex(x^2 + 1)  # 'x^{2} + 1'"],
        "category": "utility",
    },
    "plot": {
        "signature": "plot(f, xrange, **options)",
        "description": "Plot a function.",
        "params": [
            {"name": "f", "type": "function", "description": "Function to plot", "default": None},
            {"name": "xrange", "type": "tuple", "description": "Range (x, xmin, xmax)", "default": None},
        ],
        "returns": "Graphics",
        "examples": ["var('x'); plot(sin(x), (x, -pi, pi))"],
        "category": "plotting",
    },
}


# ============== Method Documentation for Classes ==============

METHOD_DOCS: dict[str, dict[str, dict]] = {
    "Matrix": {
        "det": {"signature": "det()", "description": "Return determinant.", "returns": "element"},
        "inverse": {"signature": "inverse()", "description": "Return inverse matrix.", "returns": "Matrix"},
        "transpose": {"signature": "transpose()", "description": "Return transpose.", "returns": "Matrix"},
        "trace": {"signature": "trace()", "description": "Return trace.", "returns": "element"},
        "rank": {"signature": "rank()", "description": "Return rank.", "returns": "integer"},
        "nrows": {"signature": "nrows()", "description": "Return number of rows.", "returns": "integer"},
        "ncols": {"signature": "ncols()", "description": "Return number of columns.", "returns": "integer"},
        "solve_right": {"signature": "solve_right(B)", "description": "Solve A*X = B.", "returns": "Matrix/Vector"},
        "solve_left": {"signature": "solve_left(B)", "description": "Solve X*A = B.", "returns": "Matrix/Vector"},
        "kernel": {"signature": "kernel()", "description": "Return kernel.", "returns": "FreeModule"},
        "eigenvalues": {"signature": "eigenvalues()", "description": "Return eigenvalues.", "returns": "list"},
        "eigenvectors_right": {"signature": "eigenvectors_right()", "description": "Return eigenvectors.", "returns": "list"},
        "charpoly": {"signature": "charpoly(var='x')", "description": "Return characteristic polynomial.", "returns": "polynomial"},
        "minpoly": {"signature": "minpoly(var='x')", "description": "Return minimal polynomial.", "returns": "polynomial"},
        "echelon_form": {"signature": "echelon_form()", "description": "Return echelon form.", "returns": "Matrix"},
        "jordan_form": {"signature": "jordan_form()", "description": "Return Jordan normal form.", "returns": "Matrix"},
        "smith_form": {"signature": "smith_form()", "description": "Return Smith normal form.", "returns": "Matrix"},
        "LLL": {"signature": "LLL(delta=0.99)", "description": "LLL reduction for lattice attacks.", "returns": "Matrix"},
        "BKZ": {"signature": "BKZ(block_size=10)", "description": "BKZ reduction (stronger than LLL).", "returns": "Matrix"},
        "gram_schmidt": {"signature": "gram_schmidt()", "description": "Gram-Schmidt orthogonalization.", "returns": "tuple"},
        "augment": {"signature": "augment(other)", "description": "Augment horizontally.", "returns": "Matrix"},
        "stack": {"signature": "stack(other)", "description": "Stack vertically.", "returns": "Matrix"},
        "change_ring": {"signature": "change_ring(ring)", "description": "Change base ring.", "returns": "Matrix"},
    },
    "EllipticCurve": {
        "order": {"signature": "order()", "description": "Return curve order.", "returns": "integer"},
        "abelian_group": {"signature": "abelian_group()", "description": "Return group structure.", "returns": "AbelianGroup"},
        "gens": {"signature": "gens()", "description": "Return generators.", "returns": "list"},
        "random_point": {"signature": "random_point()", "description": "Return random point.", "returns": "Point"},
        "points": {"signature": "points()", "description": "Return all points.", "returns": "list"},
        "lift_x": {"signature": "lift_x(x)", "description": "Find point with given x.", "returns": "Point"},
        "j_invariant": {"signature": "j_invariant()", "description": "Return j-invariant.", "returns": "element"},
        "discriminant": {"signature": "discriminant()", "description": "Return discriminant.", "returns": "element"},
    },
    "Ideal": {
        "groebner_basis": {"signature": "groebner_basis()", "description": "Compute Gröbner basis.", "returns": "list"},
        "dimension": {"signature": "dimension()", "description": "Return dimension.", "returns": "integer"},
        "variety": {"signature": "variety()", "description": "Return variety.", "returns": "list"},
        "reduce": {"signature": "reduce(f)", "description": "Reduce f modulo ideal.", "returns": "element"},
        "gens": {"signature": "gens()", "description": "Return generators.", "returns": "list"},
    },
    "PolynomialRing": {
        "gen": {"signature": "gen()", "description": "Return generator.", "returns": "polynomial"},
        "gens": {"signature": "gens()", "description": "Return all generators.", "returns": "tuple"},
        "ideal": {"signature": "ideal(gens)", "description": "Create ideal.", "returns": "Ideal"},
    },
    "FiniteField": {
        "order": {"signature": "order()", "description": "Return field order.", "returns": "integer"},
        "characteristic": {"signature": "characteristic()", "description": "Return characteristic.", "returns": "integer"},
        "gen": {"signature": "gen()", "description": "Return generator.", "returns": "element"},
        "random_element": {"signature": "random_element()", "description": "Return random element.", "returns": "element"},
        "multiplicative_generator": {"signature": "multiplicative_generator()", "description": "Return primitive root.", "returns": "element"},
    },
}


def get_function_doc(name: str) -> Optional[FunctionDoc]:
    """Get documentation for a function by name."""
    return FUNCTION_DOCS.get(name)


def get_method_doc(class_name: str, method_name: str) -> Optional[dict]:
    """Get documentation for a class method."""
    if class_name in METHOD_DOCS:
        return METHOD_DOCS[class_name].get(method_name)
    return None


def get_all_function_names() -> list[str]:
    """Get all documented function names."""
    return list(FUNCTION_DOCS.keys())


def get_class_methods(class_name: str) -> list[str]:
    """Get all documented methods for a class."""
    if class_name in METHOD_DOCS:
        return list(METHOD_DOCS[class_name].keys())
    return []


def format_hover_markdown(name: str, doc: FunctionDoc) -> str:
    """Format function documentation as Markdown for hover display."""
    lines = [
        f"### {name}",
        "",
        f"```python",
        f"{doc['signature']}",
        f"```",
        "",
        doc["description"],
        "",
    ]
    
    if doc["params"]:
        lines.append("**Parameters:**")
        for p in doc["params"]:
            default = f" (default: {p['default']})" if p.get("default") else ""
            lines.append(f"- `{p['name']}` ({p['type']}): {p['description']}{default}")
        lines.append("")
    
    lines.append(f"**Returns:** {doc['returns']}")
    lines.append("")
    
    if doc["examples"]:
        lines.append("**Examples:**")
        lines.append("```python")
        lines.extend(doc["examples"])
        lines.append("```")
    
    return "\n".join(lines)


def format_method_hover(class_name: str, method_name: str, doc: dict) -> str:
    """Format method documentation as Markdown for hover display."""
    lines = [
        f"### {class_name}.{method_name}",
        "",
        f"```python",
        f"{doc['signature']}",
        f"```",
        "",
        doc["description"],
        "",
        f"**Returns:** {doc['returns']}",
    ]
    return "\n".join(lines)
