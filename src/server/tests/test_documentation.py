"""
Unit tests for documentation.py - Documentation helper functions.
Tests function and method documentation retrieval and formatting.
"""

from __future__ import annotations
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from documentation import (
    FUNCTION_DOCS, METHOD_DOCS,
    get_function_doc, get_method_doc,
    get_all_function_names, get_class_methods,
    format_hover_markdown, format_method_hover,
    FunctionDoc, ParameterDoc
)


class TestFunctionDocs:
    """Tests for FUNCTION_DOCS data structure."""
    
    def test_function_docs_not_empty(self):
        """Test FUNCTION_DOCS is not empty."""
        assert len(FUNCTION_DOCS) > 0
    
    def test_function_doc_structure(self):
        """Test function doc has required fields."""
        for name, doc in FUNCTION_DOCS.items():
            assert "signature" in doc, f"{name} missing signature"
            assert "description" in doc, f"{name} missing description"
            assert "params" in doc, f"{name} missing params"
            assert "returns" in doc, f"{name} missing returns"
            assert "examples" in doc, f"{name} missing examples"
            assert "category" in doc, f"{name} missing category"
    
    def test_factor_function_exists(self):
        """Test factor function is documented."""
        assert "factor" in FUNCTION_DOCS
    
    def test_gcd_function_exists(self):
        """Test gcd function is documented."""
        assert "gcd" in FUNCTION_DOCS
    
    def test_matrix_function_exists(self):
        """Test matrix function is documented."""
        assert "matrix" in FUNCTION_DOCS
    
    def test_elliptic_curve_exists(self):
        """Test EllipticCurve is documented."""
        assert "EllipticCurve" in FUNCTION_DOCS


class TestMethodDocs:
    """Tests for METHOD_DOCS data structure."""
    
    def test_method_docs_not_empty(self):
        """Test METHOD_DOCS is not empty."""
        assert len(METHOD_DOCS) > 0
    
    def test_matrix_methods_exist(self):
        """Test Matrix class has methods documented."""
        assert "Matrix" in METHOD_DOCS
        assert len(METHOD_DOCS["Matrix"]) > 0
    
    def test_elliptic_curve_methods_exist(self):
        """Test EllipticCurve class has methods documented."""
        assert "EllipticCurve" in METHOD_DOCS
    
    def test_method_doc_structure(self):
        """Test method docs have required fields."""
        for class_name, methods in METHOD_DOCS.items():
            for method_name, doc in methods.items():
                assert "signature" in doc, f"{class_name}.{method_name} missing signature"
                assert "description" in doc, f"{class_name}.{method_name} missing description"
                assert "returns" in doc, f"{class_name}.{method_name} missing returns"


class TestGetFunctionDoc:
    """Tests for get_function_doc function."""
    
    def test_existing_function(self):
        """Test getting doc for existing function."""
        doc = get_function_doc("factor")
        assert doc is not None
        assert "signature" in doc
        assert "factor" in doc["signature"]
    
    def test_nonexistent_function(self):
        """Test getting doc for nonexistent function."""
        doc = get_function_doc("nonexistent_function_xyz")
        assert doc is None
    
    def test_gcd_function_doc(self):
        """Test gcd function documentation."""
        doc = get_function_doc("gcd")
        assert doc is not None
        assert "greatest common divisor" in doc["description"].lower()
    
    def test_matrix_function_doc(self):
        """Test matrix function documentation."""
        doc = get_function_doc("matrix")
        assert doc is not None
        assert doc["category"] == "linear_algebra"
    
    def test_crt_function_doc(self):
        """Test crt (Chinese Remainder Theorem) documentation."""
        doc = get_function_doc("crt")
        assert doc is not None
        assert doc["category"] == "cryptography"
    
    def test_function_doc_params(self):
        """Test function doc has parameters."""
        doc = get_function_doc("factor")
        assert doc is not None
        assert len(doc["params"]) > 0
        # First param should have required fields
        param = doc["params"][0]
        assert "name" in param
        assert "type" in param
        assert "description" in param
    
    def test_function_doc_examples(self):
        """Test function doc has examples."""
        doc = get_function_doc("factor")
        assert doc is not None
        assert len(doc["examples"]) > 0


class TestGetMethodDoc:
    """Tests for get_method_doc function."""
    
    def test_existing_method(self):
        """Test getting doc for existing method."""
        doc = get_method_doc("Matrix", "det")
        assert doc is not None
        assert "signature" in doc
    
    def test_nonexistent_class(self):
        """Test getting doc for nonexistent class."""
        doc = get_method_doc("NonexistentClass", "method")
        assert doc is None
    
    def test_nonexistent_method(self):
        """Test getting doc for nonexistent method."""
        doc = get_method_doc("Matrix", "nonexistent_method")
        assert doc is None
    
    def test_matrix_inverse_method(self):
        """Test Matrix.inverse method documentation."""
        doc = get_method_doc("Matrix", "inverse")
        assert doc is not None
        assert "inverse" in doc["description"].lower()
    
    def test_matrix_lll_method(self):
        """Test Matrix.LLL method documentation."""
        doc = get_method_doc("Matrix", "LLL")
        assert doc is not None
        assert "LLL" in doc["signature"]
    
    def test_elliptic_curve_order_method(self):
        """Test EllipticCurve.order method documentation."""
        doc = get_method_doc("EllipticCurve", "order")
        assert doc is not None


class TestGetAllFunctionNames:
    """Tests for get_all_function_names function."""
    
    def test_returns_list(self):
        """Test returns a list."""
        names = get_all_function_names()
        assert isinstance(names, list)
    
    def test_not_empty(self):
        """Test list is not empty."""
        names = get_all_function_names()
        assert len(names) > 0
    
    def test_contains_common_functions(self):
        """Test contains common SageMath functions."""
        names = get_all_function_names()
        assert "factor" in names
        assert "gcd" in names
        assert "matrix" in names
    
    def test_matches_function_docs_keys(self):
        """Test matches FUNCTION_DOCS keys."""
        names = get_all_function_names()
        assert set(names) == set(FUNCTION_DOCS.keys())


class TestGetClassMethods:
    """Tests for get_class_methods function."""
    
    def test_matrix_methods(self):
        """Test getting Matrix methods."""
        methods = get_class_methods("Matrix")
        assert isinstance(methods, list)
        assert len(methods) > 0
        assert "det" in methods
        assert "inverse" in methods
    
    def test_elliptic_curve_methods(self):
        """Test getting EllipticCurve methods."""
        methods = get_class_methods("EllipticCurve")
        assert isinstance(methods, list)
        assert len(methods) > 0
        assert "order" in methods
    
    def test_nonexistent_class(self):
        """Test getting methods for nonexistent class."""
        methods = get_class_methods("NonexistentClass")
        assert methods == []
    
    def test_ideal_methods(self):
        """Test getting Ideal methods."""
        methods = get_class_methods("Ideal")
        assert "groebner_basis" in methods


class TestFormatHoverMarkdown:
    """Tests for format_hover_markdown function."""
    
    def test_basic_formatting(self):
        """Test basic markdown formatting."""
        doc = get_function_doc("factor")
        markdown = format_hover_markdown("factor", doc)
        assert "### factor" in markdown
        assert "```python" in markdown
        assert "```" in markdown
    
    def test_contains_signature(self):
        """Test markdown contains signature."""
        doc = get_function_doc("gcd")
        markdown = format_hover_markdown("gcd", doc)
        assert doc["signature"] in markdown
    
    def test_contains_description(self):
        """Test markdown contains description."""
        doc = get_function_doc("gcd")
        markdown = format_hover_markdown("gcd", doc)
        assert doc["description"] in markdown
    
    def test_contains_parameters(self):
        """Test markdown contains parameters section."""
        doc = get_function_doc("factor")
        markdown = format_hover_markdown("factor", doc)
        assert "**Parameters:**" in markdown
    
    def test_contains_returns(self):
        """Test markdown contains returns section."""
        doc = get_function_doc("factor")
        markdown = format_hover_markdown("factor", doc)
        assert "**Returns:**" in markdown
    
    def test_contains_examples(self):
        """Test markdown contains examples."""
        doc = get_function_doc("factor")
        markdown = format_hover_markdown("factor", doc)
        assert "**Examples:**" in markdown
    
    def test_parameter_with_default(self):
        """Test parameter with default value is formatted."""
        doc = get_function_doc("is_prime")
        markdown = format_hover_markdown("is_prime", doc)
        # Should contain default info if param has default
        for param in doc["params"]:
            if param.get("default"):
                assert "default" in markdown.lower()
                break


class TestFormatMethodHover:
    """Tests for format_method_hover function."""
    
    def test_basic_formatting(self):
        """Test basic method hover formatting."""
        doc = get_method_doc("Matrix", "det")
        markdown = format_method_hover("Matrix", "det", doc)
        assert "### Matrix.det" in markdown
    
    def test_contains_signature(self):
        """Test markdown contains signature."""
        doc = get_method_doc("Matrix", "inverse")
        markdown = format_method_hover("Matrix", "inverse", doc)
        assert doc["signature"] in markdown
    
    def test_contains_description(self):
        """Test markdown contains description."""
        doc = get_method_doc("Matrix", "det")
        markdown = format_method_hover("Matrix", "det", doc)
        assert doc["description"] in markdown
    
    def test_contains_returns(self):
        """Test markdown contains returns."""
        doc = get_method_doc("Matrix", "rank")
        markdown = format_method_hover("Matrix", "rank", doc)
        assert "**Returns:**" in markdown
    
    def test_code_block_present(self):
        """Test code block is present."""
        doc = get_method_doc("Matrix", "det")
        markdown = format_method_hover("Matrix", "det", doc)
        assert "```python" in markdown
        assert "```" in markdown


class TestDocumentationCategories:
    """Tests for documentation categories."""
    
    def test_number_theory_functions(self):
        """Test number theory functions exist."""
        number_theory_funcs = [
            name for name, doc in FUNCTION_DOCS.items()
            if doc["category"] == "number_theory"
        ]
        assert len(number_theory_funcs) > 0
        assert "factor" in number_theory_funcs
        assert "gcd" in number_theory_funcs
    
    def test_cryptography_functions(self):
        """Test cryptography functions exist."""
        crypto_funcs = [
            name for name, doc in FUNCTION_DOCS.items()
            if doc["category"] == "cryptography"
        ]
        assert len(crypto_funcs) > 0
        assert "crt" in crypto_funcs
        assert "inverse_mod" in crypto_funcs
    
    def test_linear_algebra_functions(self):
        """Test linear algebra functions exist."""
        linalg_funcs = [
            name for name, doc in FUNCTION_DOCS.items()
            if doc["category"] == "linear_algebra"
        ]
        assert len(linalg_funcs) > 0
        assert "matrix" in linalg_funcs
        assert "vector" in linalg_funcs
    
    def test_symbolic_functions(self):
        """Test symbolic functions exist."""
        symbolic_funcs = [
            name for name, doc in FUNCTION_DOCS.items()
            if doc["category"] == "symbolic"
        ]
        assert len(symbolic_funcs) > 0
        assert "var" in symbolic_funcs
        assert "solve" in symbolic_funcs
    
    def test_calculus_functions(self):
        """Test calculus functions exist."""
        calculus_funcs = [
            name for name, doc in FUNCTION_DOCS.items()
            if doc["category"] == "calculus"
        ]
        assert len(calculus_funcs) > 0
        assert "diff" in calculus_funcs
        assert "integrate" in calculus_funcs


class TestDocumentationCompleteness:
    """Tests for documentation completeness."""
    
    def test_all_params_have_names(self):
        """Test all parameters have names."""
        for func_name, doc in FUNCTION_DOCS.items():
            for param in doc["params"]:
                assert "name" in param and param["name"], f"{func_name} has param without name"
    
    def test_all_params_have_types(self):
        """Test all parameters have types."""
        for func_name, doc in FUNCTION_DOCS.items():
            for param in doc["params"]:
                assert "type" in param and param["type"], f"{func_name} has param without type"
    
    def test_all_params_have_descriptions(self):
        """Test all parameters have descriptions."""
        for func_name, doc in FUNCTION_DOCS.items():
            for param in doc["params"]:
                assert "description" in param and param["description"], \
                    f"{func_name} has param without description"
    
    def test_signatures_not_empty(self):
        """Test all signatures are not empty."""
        for func_name, doc in FUNCTION_DOCS.items():
            assert doc["signature"].strip(), f"{func_name} has empty signature"
    
    def test_descriptions_not_empty(self):
        """Test all descriptions are not empty."""
        for func_name, doc in FUNCTION_DOCS.items():
            assert doc["description"].strip(), f"{func_name} has empty description"
