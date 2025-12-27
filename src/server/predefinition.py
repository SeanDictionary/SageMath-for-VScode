# For identify tokens
TOKEN_TYPES = ["namespace", "type", "class", "function", "variable", "parameter", "property", "method", "keyword", "modifier", "operator", "string", "number", "comment"]
TOKEN_MODIFIERS = ["declaration", "definition", "readonly", "static", "deprecated", "defaultLibrary"]

# For classify tokens
KEYWORDS = {
    "for", "if", "else", "while", "return", "import", "from", "as", "try", "except",
    "finally", "with", "yield", "def", "class", "lambda", "assert", "break", "continue",
    "pass", "global", "nonlocal", "del", "raise", "in", "is", "not", "and", "or",
    "True", "False", "None", "self"
}

# Predefined sets for SageMath Std functions and classes
FUNCTIONS = {"GCD", "crt", "diagonal_matrix", "block_matrix", "identity_matrix", "zero_matrix", "random_matrix",}
CLASSES = {
    "ZZ": {"methods": [], "properties": {}},
    "QQ": {"methods": [], "properties": {}},
    "RR": {"methods": [], "properties": {}},
    "CC": {"methods": [], "properties": {}},
    "Zmod": {"methods": [], "properties": {}},
    "GF": {"methods": [], "properties": {}},
    "PolynomialRing": {"methods": [], "properties": {}},
    "Ideal": {"methods": ["groebner_basis"], "properties": {}},
    "Matrix": {"methods": ["nrows", "ncols", "det", "rows", "columns", "solve_right", "solve_left", "LLL", "BKZ"], "properties": {}},
    "vector": {"methods": [], "properties": {}},
    "var": {"methods": [], "properties": {}},
}
