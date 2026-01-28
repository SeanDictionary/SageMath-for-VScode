# For identify tokens
TOKEN_TYPES = ["namespace", "type", "class", "function", "variable", "parameter", "property", "method", "keyword", "modifier", "operator", "string", "number", "comment"]
TOKEN_MODIFIERS = ["declaration", "definition", "readonly", "static", "deprecated", "defaultLibrary"]

# For classify tokens
KEYWORDS = {
    "for", "if", "else", "elif", "while", "return", "import", "from", "as", "try", "except",
    "finally", "with", "yield", "def", "class", "lambda", "assert", "break", "continue",
    "pass", "global", "nonlocal", "del", "raise", "in", "is", "not", "and", "or",
    "True", "False", "None", "self", "async", "await"
}

# Predefined sets for SageMath Std functions and classes
# Reference: https://doc.sagemath.org/html/en/reference/index.html

# ============== Mathematical Functions ==============
FUNCTIONS = {
    # Basic arithmetic
    "GCD", "gcd", "LCM", "lcm", "xgcd", "crt", "factor", "prime_factors",
    "divisors", "is_prime", "next_prime", "previous_prime", "nth_prime",
    "prime_range", "primes", "factorial", "binomial", "fibonacci", "lucas_number1",
    
    # Number theory
    "euler_phi", "moebius", "sigma", "kronecker", "legendre_symbol",
    "jacobi_symbol", "quadratic_residues", "primitive_root", "order_from_multiple",
    "discrete_log", "power_mod", "inverse_mod", "mod", "Mod",
    
    # Algebraic operations
    "expand", "factor", "simplify", "simplify_full", "collect", "combine",
    "radsimp", "ratsimp", "trigsimp", "powsimp", "logcombine",
    
    # Calculus
    "diff", "derivative", "integrate", "integral", "limit", "taylor", "series",
    "laplace", "inverse_laplace", "fourier", "inverse_fourier",
    
    # Solving equations
    "solve", "solve_mod", "roots", "real_roots", "complex_roots",
    "find_root", "find_local_minimum", "find_local_maximum",
    
    # Linear algebra functions
    "matrix", "Matrix", "vector", "identity_matrix", "zero_matrix", "ones_matrix",
    "diagonal_matrix", "block_matrix", "block_diagonal_matrix", "random_matrix",
    "elementary_matrix", "companion_matrix", "jordan_block",
    
    # Polynomial functions
    "poly", "degree", "coefficients", "roots", "resultant", "discriminant",
    "content", "primitive_part", "squarefree_decomposition",
    
    # Combinatorics
    "permutations", "combinations", "arrangements", "derangements",
    "partitions", "Partitions", "compositions", "catalan_number",
    "bell_number", "bernoulli", "stirling_number1", "stirling_number2",
    
    # Graph theory
    "Graph", "DiGraph", "graphs", "digraphs",
    
    # Number fields and rings
    "NumberField", "QuadraticField", "CyclotomicField",
    "FunctionField", "FractionField",
    
    # Cryptographic functions (CTF related)
    "bytes_to_long", "long_to_bytes", "inverse_mod", "discrete_log",
    "crt", "power_mod", "random_prime", "is_prime_power",
    
    # Elliptic curves
    "EllipticCurve", "EllipticCurve_from_j",
    
    # Lattices
    "IntegerLattice", "FreeModule",
    
    # Plotting
    "plot", "list_plot", "scatter_plot", "line", "circle", "polygon",
    "parametric_plot", "polar_plot", "implicit_plot", "contour_plot",
    "plot3d", "implicit_plot3d", "parametric_plot3d",
    
    # Symbolic
    "var", "assume", "forget", "assumptions", "symbolic_expression",
    "SR", "Expression",
    
    # Utilities
    "show", "pretty_print", "latex", "html", "save", "load",
    "randint", "random", "set_random_seed", "ceil", "floor", "round",
    "abs", "sign", "sqrt", "log", "ln", "exp", "sin", "cos", "tan",
    "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh",
    "pi", "e", "I", "oo", "infinity",
    
    # Type conversions
    "int", "float", "complex", "Integer", "Rational", "RealNumber",
    "ComplexNumber", "RealField", "ComplexField",
    
    # Pari/GP interface
    "pari", "gp",
}

# ============== Classes and Types ==============
CLASSES = {
    # Base rings
    "ZZ": {"methods": ["quo", "random_element", "ideal", "fraction_field"], "properties": {}},
    "QQ": {"methods": ["random_element", "algebraic_closure"], "properties": {}},
    "RR": {"methods": ["random_element", "precision"], "properties": {}},
    "CC": {"methods": ["random_element", "precision"], "properties": {}},
    "RDF": {"methods": ["random_element"], "properties": {}},
    "CDF": {"methods": ["random_element"], "properties": {}},
    "RIF": {"methods": [], "properties": {}},
    "CIF": {"methods": [], "properties": {}},
    
    # Modular arithmetic
    "Zmod": {"methods": ["order", "unit_group", "random_element"], "properties": {}},
    "IntegerModRing": {"methods": ["order", "unit_group", "random_element"], "properties": {}},
    "GF": {"methods": ["order", "characteristic", "degree", "gen", "random_element", "multiplicative_generator"], "properties": {}},
    "FiniteField": {"methods": ["order", "characteristic", "degree", "gen", "random_element"], "properties": {}},
    
    # Polynomial rings
    "PolynomialRing": {"methods": ["gen", "gens", "ngens", "random_element", "ideal", "quo"], "properties": {}},
    "Polynomial": {"methods": ["degree", "coefficients", "roots", "factor", "gcd", "lcm", "derivative", "integral", "resultant", "discriminant", "is_irreducible", "is_squarefree"], "properties": {}},
    
    # Ideals
    "Ideal": {"methods": ["groebner_basis", "dimension", "variety", "reduce", "gens", "is_zero", "is_one", "is_prime", "is_maximal", "is_principal", "radical", "saturation"], "properties": {}},
    
    # Matrix
    "Matrix": {
        "methods": [
            "nrows", "ncols", "det", "determinant", "trace", "rank", "nullity",
            "rows", "columns", "row", "column", "transpose", "T", "conjugate", "H",
            "inverse", "adjugate", "adjoint", "pseudoinverse",
            "solve_right", "solve_left", "right_kernel", "left_kernel", "kernel", "image",
            "eigenvalues", "eigenvectors_right", "eigenvectors_left", "eigenspaces_right", "eigenspaces_left",
            "characteristic_polynomial", "minimal_polynomial", "charpoly", "minpoly",
            "jordan_form", "rational_form", "smith_form", "hermite_form", "echelon_form",
            "LU", "QR", "SVD", "cholesky",
            "LLL", "BKZ", "gram_schmidt",
            "norm", "is_symmetric", "is_hermitian", "is_positive_definite",
            "is_square", "is_invertible", "is_singular",
            "augment", "stack", "submatrix", "matrix_from_rows", "matrix_from_columns",
            "change_ring", "base_ring", "dense_matrix", "sparse_matrix",
            "apply_map", "list", "dict"
        ],
        "properties": {}
    },
    
    # Vector
    "vector": {"methods": ["dot_product", "cross_product", "norm", "normalized", "inner_product", "outer_product", "pairwise_product"], "properties": {}},
    "FreeModule": {"methods": ["basis", "dimension", "gens", "submodule", "quotient"], "properties": {}},
    
    # Symbolic
    "var": {"methods": [], "properties": {}},
    "SR": {"methods": ["var", "symbol"], "properties": {}},
    "Expression": {"methods": ["simplify", "expand", "factor", "collect", "subs", "substitute", "diff", "derivative", "integrate", "limit", "series", "taylor", "solve", "roots", "real", "imag", "abs", "conjugate"], "properties": {}},
    
    # Number fields
    "NumberField": {"methods": ["degree", "discriminant", "signature", "gen", "gens", "ring_of_integers", "class_number", "class_group", "unit_group", "units", "galois_group"], "properties": {}},
    "QuadraticField": {"methods": ["degree", "discriminant", "gen", "ring_of_integers"], "properties": {}},
    
    # Elliptic curves
    "EllipticCurve": {
        "methods": [
            "order", "abelian_group", "gens", "rational_points", "lift_x",
            "a_invariants", "b_invariants", "c_invariants", "j_invariant", "discriminant",
            "is_singular", "is_supersingular", "is_ordinary",
            "point", "random_point", "points",
            "multiplication_by_m", "division_polynomial",
            "torsion_order", "torsion_points", "torsion_subgroup",
            "height", "height_pairing_matrix", "regulator",
            "rank", "gens", "saturation", "descent",
            "isogeny", "isogenies_prime_degree", "isogeny_class"
        ],
        "properties": {}
    },
    
    # Groups
    "AbelianGroup": {"methods": ["order", "gens", "gen", "invariants", "is_cyclic"], "properties": {}},
    "PermutationGroup": {"methods": ["order", "gens", "gen", "degree", "orbits", "is_abelian", "is_cyclic", "is_transitive"], "properties": {}},
    "SymmetricGroup": {"methods": ["order", "gens", "degree"], "properties": {}},
    "CyclicPermutationGroup": {"methods": ["order", "gen"], "properties": {}},
    "DihedralGroup": {"methods": ["order", "gens"], "properties": {}},
    
    # Graphs
    "Graph": {"methods": ["vertices", "edges", "neighbors", "degree", "order", "size", "is_connected", "is_tree", "is_bipartite", "chromatic_number", "clique_number", "diameter", "shortest_path", "adjacency_matrix", "laplacian_matrix"], "properties": {}},
    "DiGraph": {"methods": ["vertices", "edges", "in_degree", "out_degree", "order", "size", "is_connected", "strongly_connected_components", "topological_sort", "adjacency_matrix"], "properties": {}},
    
    # Power series
    "PowerSeriesRing": {"methods": ["gen", "default_prec"], "properties": {}},
    "LaurentSeriesRing": {"methods": ["gen"], "properties": {}},
    
    # Integers and Rationals
    "Integer": {"methods": ["factor", "divisors", "is_prime", "is_prime_power", "is_perfect_power", "sqrt", "nth_root", "digits", "binary", "bits", "nbits", "popcount"], "properties": {}},
    "Rational": {"methods": ["numerator", "denominator", "floor", "ceil", "round", "sign", "abs"], "properties": {}},
    
    # Sequences
    "Sequence": {"methods": [], "properties": {}},
    "OEIS": {"methods": ["find_by_id", "find_by_sequence"], "properties": {}},
}
