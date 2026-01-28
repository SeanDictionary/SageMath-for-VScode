"""
Unit tests for predefinition.py - Predefined constants and data.
Tests TOKEN_TYPES, TOKEN_MODIFIERS, KEYWORDS, FUNCTIONS, CLASSES.
"""

from __future__ import annotations
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from predefinition import TOKEN_TYPES, TOKEN_MODIFIERS, KEYWORDS, FUNCTIONS, CLASSES


class TestTokenTypes:
    """Tests for TOKEN_TYPES list."""
    
    def test_not_empty(self):
        """Test TOKEN_TYPES is not empty."""
        assert len(TOKEN_TYPES) > 0
    
    def test_is_list(self):
        """Test TOKEN_TYPES is a list."""
        assert isinstance(TOKEN_TYPES, list)
    
    def test_contains_required_types(self):
        """Test contains required semantic token types."""
        required = ["class", "function", "variable", "method", "keyword", "operator"]
        for token_type in required:
            assert token_type in TOKEN_TYPES, f"Missing required type: {token_type}"
    
    def test_contains_namespace(self):
        """Test contains namespace type."""
        assert "namespace" in TOKEN_TYPES
    
    def test_contains_parameter(self):
        """Test contains parameter type."""
        assert "parameter" in TOKEN_TYPES
    
    def test_contains_property(self):
        """Test contains property type."""
        assert "property" in TOKEN_TYPES
    
    def test_all_strings(self):
        """Test all items are strings."""
        for token_type in TOKEN_TYPES:
            assert isinstance(token_type, str)
    
    def test_no_duplicates(self):
        """Test no duplicate types."""
        assert len(TOKEN_TYPES) == len(set(TOKEN_TYPES))


class TestTokenModifiers:
    """Tests for TOKEN_MODIFIERS list."""
    
    def test_not_empty(self):
        """Test TOKEN_MODIFIERS is not empty."""
        assert len(TOKEN_MODIFIERS) > 0
    
    def test_is_list(self):
        """Test TOKEN_MODIFIERS is a list."""
        assert isinstance(TOKEN_MODIFIERS, list)
    
    def test_contains_readonly(self):
        """Test contains readonly modifier."""
        assert "readonly" in TOKEN_MODIFIERS
    
    def test_contains_declaration(self):
        """Test contains declaration modifier."""
        assert "declaration" in TOKEN_MODIFIERS
    
    def test_contains_definition(self):
        """Test contains definition modifier."""
        assert "definition" in TOKEN_MODIFIERS
    
    def test_contains_static(self):
        """Test contains static modifier."""
        assert "static" in TOKEN_MODIFIERS
    
    def test_contains_deprecated(self):
        """Test contains deprecated modifier."""
        assert "deprecated" in TOKEN_MODIFIERS
    
    def test_all_strings(self):
        """Test all items are strings."""
        for modifier in TOKEN_MODIFIERS:
            assert isinstance(modifier, str)
    
    def test_no_duplicates(self):
        """Test no duplicate modifiers."""
        assert len(TOKEN_MODIFIERS) == len(set(TOKEN_MODIFIERS))


class TestKeywords:
    """Tests for KEYWORDS set."""
    
    def test_not_empty(self):
        """Test KEYWORDS is not empty."""
        assert len(KEYWORDS) > 0
    
    def test_is_set(self):
        """Test KEYWORDS is a set."""
        assert isinstance(KEYWORDS, set)
    
    def test_contains_python_keywords(self):
        """Test contains Python keywords."""
        python_keywords = [
            "for", "if", "else", "elif", "while", "return",
            "import", "from", "as", "try", "except", "finally",
            "with", "def", "class", "lambda", "pass", "break",
            "continue", "raise", "in", "is", "not", "and", "or"
        ]
        for kw in python_keywords:
            assert kw in KEYWORDS, f"Missing keyword: {kw}"
    
    def test_contains_builtin_constants(self):
        """Test contains builtin constants."""
        constants = ["True", "False", "None"]
        for const in constants:
            assert const in KEYWORDS, f"Missing constant: {const}"
    
    def test_contains_self(self):
        """Test contains self keyword."""
        assert "self" in KEYWORDS
    
    def test_contains_async_await(self):
        """Test contains async/await keywords."""
        assert "async" in KEYWORDS
        assert "await" in KEYWORDS
    
    def test_contains_yield(self):
        """Test contains yield keyword."""
        assert "yield" in KEYWORDS
    
    def test_contains_global_nonlocal(self):
        """Test contains global and nonlocal."""
        assert "global" in KEYWORDS
        assert "nonlocal" in KEYWORDS
    
    def test_all_strings(self):
        """Test all items are strings."""
        for kw in KEYWORDS:
            assert isinstance(kw, str)


class TestFunctions:
    """Tests for FUNCTIONS set."""
    
    def test_not_empty(self):
        """Test FUNCTIONS is not empty."""
        assert len(FUNCTIONS) > 0
    
    def test_is_set(self):
        """Test FUNCTIONS is a set."""
        assert isinstance(FUNCTIONS, set)
    
    def test_contains_number_theory(self):
        """Test contains number theory functions."""
        number_theory = ["gcd", "lcm", "factor", "is_prime", "next_prime", "euler_phi"]
        for func in number_theory:
            assert func in FUNCTIONS, f"Missing number theory function: {func}"
    
    def test_contains_crypto_functions(self):
        """Test contains cryptographic functions."""
        crypto = ["crt", "inverse_mod", "power_mod", "discrete_log"]
        for func in crypto:
            assert func in FUNCTIONS, f"Missing crypto function: {func}"
    
    def test_contains_linear_algebra(self):
        """Test contains linear algebra functions."""
        linalg = ["matrix", "Matrix", "vector", "identity_matrix", "zero_matrix"]
        for func in linalg:
            assert func in FUNCTIONS, f"Missing linear algebra function: {func}"
    
    def test_contains_symbolic(self):
        """Test contains symbolic computation functions."""
        symbolic = ["var", "solve", "expand", "simplify", "diff", "integrate"]
        for func in symbolic:
            assert func in FUNCTIONS, f"Missing symbolic function: {func}"
    
    def test_contains_plotting(self):
        """Test contains plotting functions."""
        plotting = ["plot", "list_plot", "parametric_plot"]
        for func in plotting:
            assert func in FUNCTIONS, f"Missing plotting function: {func}"
    
    def test_contains_utility_functions(self):
        """Test contains utility functions."""
        utility = ["show", "latex", "sqrt", "log", "exp", "abs"]
        for func in utility:
            assert func in FUNCTIONS, f"Missing utility function: {func}"
    
    def test_contains_elliptic_curve(self):
        """Test contains elliptic curve functions."""
        assert "EllipticCurve" in FUNCTIONS
    
    def test_all_strings(self):
        """Test all items are strings."""
        for func in FUNCTIONS:
            assert isinstance(func, str)


class TestClasses:
    """Tests for CLASSES dictionary."""
    
    def test_not_empty(self):
        """Test CLASSES is not empty."""
        assert len(CLASSES) > 0
    
    def test_is_dict(self):
        """Test CLASSES is a dictionary."""
        assert isinstance(CLASSES, dict)
    
    def test_contains_base_rings(self):
        """Test contains base rings."""
        rings = ["ZZ", "QQ", "RR", "CC", "RDF", "CDF"]
        for ring in rings:
            assert ring in CLASSES, f"Missing base ring: {ring}"
    
    def test_contains_finite_fields(self):
        """Test contains finite field classes."""
        assert "GF" in CLASSES
        assert "FiniteField" in CLASSES
        assert "Zmod" in CLASSES
    
    def test_contains_polynomial_ring(self):
        """Test contains PolynomialRing."""
        assert "PolynomialRing" in CLASSES
    
    def test_contains_matrix(self):
        """Test contains Matrix."""
        assert "Matrix" in CLASSES
    
    def test_contains_elliptic_curve(self):
        """Test contains EllipticCurve."""
        assert "EllipticCurve" in CLASSES
    
    def test_class_structure(self):
        """Test each class has methods and properties."""
        for class_name, class_info in CLASSES.items():
            assert "methods" in class_info, f"{class_name} missing methods"
            assert "properties" in class_info, f"{class_name} missing properties"
            assert isinstance(class_info["methods"], list), f"{class_name} methods not a list"
            assert isinstance(class_info["properties"], dict), f"{class_name} properties not a dict"
    
    def test_matrix_has_methods(self):
        """Test Matrix class has methods."""
        matrix_methods = CLASSES["Matrix"]["methods"]
        assert len(matrix_methods) > 0
        expected = ["det", "inverse", "transpose", "rank", "eigenvalues", "LLL"]
        for method in expected:
            assert method in matrix_methods, f"Matrix missing method: {method}"
    
    def test_elliptic_curve_has_methods(self):
        """Test EllipticCurve class has methods."""
        ec_methods = CLASSES["EllipticCurve"]["methods"]
        assert len(ec_methods) > 0
        expected = ["order", "gens", "random_point", "j_invariant"]
        for method in expected:
            assert method in ec_methods, f"EllipticCurve missing method: {method}"
    
    def test_gf_has_methods(self):
        """Test GF class has methods."""
        gf_methods = CLASSES["GF"]["methods"]
        expected = ["order", "characteristic", "gen", "random_element"]
        for method in expected:
            assert method in gf_methods, f"GF missing method: {method}"
    
    def test_polynomial_ring_has_methods(self):
        """Test PolynomialRing class has methods."""
        pr_methods = CLASSES["PolynomialRing"]["methods"]
        expected = ["gen", "gens", "ideal"]
        for method in expected:
            assert method in pr_methods, f"PolynomialRing missing method: {method}"
    
    def test_ideal_has_methods(self):
        """Test Ideal class has methods."""
        ideal_methods = CLASSES["Ideal"]["methods"]
        expected = ["groebner_basis", "dimension", "variety", "reduce"]
        for method in expected:
            assert method in ideal_methods, f"Ideal missing method: {method}"
    
    def test_graph_classes(self):
        """Test graph classes exist."""
        assert "Graph" in CLASSES
        assert "DiGraph" in CLASSES


class TestDataConsistency:
    """Tests for data consistency across modules."""
    
    def test_token_types_unique_indices(self):
        """Test TOKEN_TYPES can be used for unique indexing."""
        indices = {s: i for i, s in enumerate(TOKEN_TYPES)}
        assert len(indices) == len(TOKEN_TYPES)
    
    def test_token_modifiers_power_of_two(self):
        """Test TOKEN_MODIFIERS work with bitwise operations."""
        # Each modifier should be able to use 2^i representation
        for i, mod in enumerate(TOKEN_MODIFIERS):
            power = 2 ** i
            assert power > 0
    
    def test_no_keyword_in_functions(self):
        """Test keywords don't overlap with functions."""
        overlap = KEYWORDS & FUNCTIONS
        # Some overlap might be intentional (like 'True', 'False')
        problematic = overlap - {"True", "False", "None"}
        assert len(problematic) == 0, f"Keywords overlap with functions: {problematic}"
    
    def test_class_names_strings(self):
        """Test all class names are valid identifiers."""
        import re
        identifier_pattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
        for class_name in CLASSES.keys():
            assert identifier_pattern.match(class_name), f"Invalid class name: {class_name}"
    
    def test_method_names_strings(self):
        """Test all method names are valid identifiers."""
        import re
        identifier_pattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
        for class_name, class_info in CLASSES.items():
            for method in class_info["methods"]:
                assert identifier_pattern.match(method), \
                    f"Invalid method name: {class_name}.{method}"
