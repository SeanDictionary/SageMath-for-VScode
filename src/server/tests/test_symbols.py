"""
Unit tests for symbols.py - Symbol extraction and analysis module.
Tests symbol extraction, type inference, and document symbol generation.
"""

from __future__ import annotations
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lsprotocol.types import SymbolKind, CompletionItemKind

from symbols import (
    SymbolExtractor,
    UserSymbol,
    extract_document_symbols,
    extract_completion_items,
)


class TestSymbolExtractor:
    """Tests for SymbolExtractor class."""
    
    def test_extract_function(self):
        """Test extracting function definitions."""
        lines = [
            "def my_function(a, b):",
            "    return a + b",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].name == "my_function"
        assert symbols[0].kind == SymbolKind.Function
        assert symbols[0].line == 0
        assert "(a, b)" in symbols[0].detail
    
    def test_extract_class(self):
        """Test extracting class definitions."""
        lines = [
            "class MyClass:",
            "    def __init__(self):",
            "        pass",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) >= 1
        class_sym = next(s for s in symbols if s.name == "MyClass")
        assert class_sym.kind == SymbolKind.Class
        assert class_sym.line == 0
    
    def test_extract_class_with_base(self):
        """Test extracting class with base class."""
        lines = [
            "class ChildClass(ParentClass):",
            "    pass",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].name == "ChildClass"
        assert "ParentClass" in symbols[0].detail
    
    def test_extract_variable(self):
        """Test extracting variable assignments."""
        lines = [
            "my_var = 42",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].name == "my_var"
        assert symbols[0].kind == SymbolKind.Variable
    
    def test_extract_multiple_variables(self):
        """Test extracting multiple variable assignment."""
        lines = [
            "a, b, c = 1, 2, 3",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 3
        names = [s.name for s in symbols]
        assert "a" in names
        assert "b" in names
        assert "c" in names
    
    def test_extract_sage_var(self):
        """Test extracting SageMath var() declarations."""
        lines = [
            "var('x y z')",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 3
        names = [s.name for s in symbols]
        assert "x" in names
        assert "y" in names
        assert "z" in names
        # Check they are marked as symbolic
        for sym in symbols:
            assert sym.inferred_type == "SR"
    
    def test_extract_polynomial_ring(self):
        """Test extracting SageMath polynomial ring definition."""
        lines = [
            "R.<x> = PolynomialRing(QQ)",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 2
        names = [s.name for s in symbols]
        assert "R" in names
        assert "x" in names
        
        r_sym = next(s for s in symbols if s.name == "R")
        assert r_sym.inferred_type == "PolynomialRing"
    
    def test_extract_polynomial_ring_multiple_vars(self):
        """Test extracting polynomial ring with multiple variables."""
        lines = [
            "R.<x, y, z> = PolynomialRing(QQ)",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 4  # R, x, y, z
        names = [s.name for s in symbols]
        assert "R" in names
        assert "x" in names
        assert "y" in names
        assert "z" in names
    
    def test_extract_finite_field(self):
        """Test extracting finite field definition."""
        lines = [
            "K.<a> = GF(2^8)",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 2
        k_sym = next(s for s in symbols if s.name == "K")
        assert k_sym.inferred_type == "GF"
    
    def test_extract_for_loop_variable(self):
        """Test extracting for loop variable."""
        lines = [
            "for i in range(10):",
            "    print(i)",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].name == "i"
        assert symbols[0].kind == SymbolKind.Variable
    
    def test_extract_with_variable(self):
        """Test extracting with-as variable."""
        lines = [
            "with open('file.txt') as f:",
            "    data = f.read()",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        # Should find f and data
        names = [s.name for s in symbols]
        assert "f" in names
    
    def test_skip_comments(self):
        """Test that comments are skipped."""
        lines = [
            "# This is a comment",
            "x = 5",
            "# Another comment",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].name == "x"
    
    def test_skip_empty_lines(self):
        """Test that empty lines are skipped."""
        lines = [
            "",
            "x = 5",
            "",
            "y = 10",
            "",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 2


class TestTypeInference:
    """Tests for type inference functionality."""
    
    def test_infer_matrix_type(self):
        """Test inferring Matrix type."""
        lines = [
            "M = matrix(ZZ, [[1, 2], [3, 4]])",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].inferred_type == "Matrix"
    
    def test_infer_vector_type(self):
        """Test inferring Vector type."""
        lines = [
            "v = vector([1, 2, 3])",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].inferred_type == "Vector"
    
    def test_infer_elliptic_curve_type(self):
        """Test inferring EllipticCurve type."""
        lines = [
            "E = EllipticCurve(GF(101), [0, 7])",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].inferred_type == "EllipticCurve"
    
    def test_infer_list_type(self):
        """Test inferring list type."""
        lines = [
            "my_list = [1, 2, 3]",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].inferred_type == "list"
    
    def test_infer_dict_type(self):
        """Test inferring dict type."""
        lines = [
            "my_dict = {'a': 1, 'b': 2}",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].inferred_type == "dict"
    
    def test_infer_integer_type(self):
        """Test inferring Integer type."""
        lines = [
            "n = Integer(42)",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].inferred_type == "Integer"
    
    def test_infer_graph_type(self):
        """Test inferring Graph type."""
        lines = [
            "G = Graph({0: [1, 2], 1: [2]})",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].inferred_type == "Graph"


class TestDocstringExtraction:
    """Tests for docstring extraction."""
    
    def test_single_line_docstring(self):
        """Test extracting single-line docstring."""
        lines = [
            'def foo():',
            '    """This is a docstring."""',
            '    pass',
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].docstring == "This is a docstring."
    
    def test_multi_line_docstring(self):
        """Test extracting multi-line docstring."""
        lines = [
            'def foo():',
            '    """',
            '    Multi-line docstring.',
            '    With more content.',
            '    """',
            '    pass',
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].docstring is not None
        assert "Multi-line" in symbols[0].docstring
    
    def test_no_docstring(self):
        """Test function without docstring."""
        lines = [
            'def foo():',
            '    x = 5',
            '    return x',
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert len(symbols) >= 1
        func_sym = next(s for s in symbols if s.name == "foo")
        assert func_sym.docstring is None


class TestDocumentSymbolConversion:
    """Tests for converting to LSP DocumentSymbol format."""
    
    def test_to_document_symbols(self):
        """Test conversion to DocumentSymbol list."""
        lines = [
            "def foo():",
            "    pass",
            "",
            "class Bar:",
            "    pass",
        ]
        extractor = SymbolExtractor()
        extractor.extract_symbols(lines)
        doc_symbols = extractor.to_document_symbols()
        
        assert len(doc_symbols) == 2
        names = [s.name for s in doc_symbols]
        assert "foo" in names
        assert "Bar" in names
    
    def test_document_symbol_ranges(self):
        """Test that DocumentSymbol ranges are correct."""
        lines = [
            "def foo():",
            "    pass",
        ]
        extractor = SymbolExtractor()
        extractor.extract_symbols(lines)
        doc_symbols = extractor.to_document_symbols()
        
        assert len(doc_symbols) == 1
        sym = doc_symbols[0]
        assert sym.range.start.line == 0
        assert sym.selection_range.start.line == 0


class TestCompletionItemConversion:
    """Tests for converting to CompletionItem format."""
    
    def test_to_completion_items(self):
        """Test conversion to CompletionItem list."""
        lines = [
            "def my_func():",
            "    pass",
            "my_var = 42",
        ]
        extractor = SymbolExtractor()
        extractor.extract_symbols(lines)
        items = extractor.to_completion_items()
        
        assert len(items) == 2
        labels = [i.label for i in items]
        assert "my_func" in labels
        assert "my_var" in labels
    
    def test_function_completion_has_parenthesis(self):
        """Test that function completion includes opening parenthesis."""
        lines = [
            "def my_func():",
            "    pass",
        ]
        extractor = SymbolExtractor()
        extractor.extract_symbols(lines)
        items = extractor.to_completion_items()
        
        assert len(items) == 1
        assert items[0].insert_text == "my_func("
        assert items[0].kind == CompletionItemKind.Function
    
    def test_variable_completion_kind(self):
        """Test that variable has correct completion kind."""
        lines = [
            "my_var = 42",
        ]
        extractor = SymbolExtractor()
        extractor.extract_symbols(lines)
        items = extractor.to_completion_items()
        
        assert len(items) == 1
        assert items[0].kind == CompletionItemKind.Variable
    
    def test_class_completion_kind(self):
        """Test that class has correct completion kind."""
        lines = [
            "class MyClass:",
            "    pass",
        ]
        extractor = SymbolExtractor()
        extractor.extract_symbols(lines)
        items = extractor.to_completion_items()
        
        assert len(items) == 1
        assert items[0].kind == CompletionItemKind.Class
    
    def test_completion_sort_text(self):
        """Test that completion items have sort text for priority."""
        lines = [
            "my_var = 42",
        ]
        extractor = SymbolExtractor()
        extractor.extract_symbols(lines)
        items = extractor.to_completion_items()
        
        assert len(items) == 1
        assert items[0].sort_text.startswith("0_")


class TestHelperFunctions:
    """Tests for module-level helper functions."""
    
    def test_extract_document_symbols(self):
        """Test extract_document_symbols convenience function."""
        lines = [
            "def foo():",
            "    pass",
        ]
        symbols = extract_document_symbols(lines)
        
        assert len(symbols) == 1
        assert symbols[0].name == "foo"
    
    def test_extract_completion_items(self):
        """Test extract_completion_items convenience function."""
        lines = [
            "my_var = 42",
        ]
        items = extract_completion_items(lines)
        
        assert len(items) == 1
        assert items[0].label == "my_var"


class TestSymbolByName:
    """Tests for getting symbols by name."""
    
    def test_get_symbol_by_name(self):
        """Test getting symbol by name."""
        lines = [
            "foo = 1",
            "bar = 2",
        ]
        extractor = SymbolExtractor()
        extractor.extract_symbols(lines)
        
        sym = extractor.get_symbol_by_name("foo")
        assert sym is not None
        assert sym.name == "foo"
    
    def test_get_nonexistent_symbol(self):
        """Test getting nonexistent symbol returns None."""
        lines = [
            "foo = 1",
        ]
        extractor = SymbolExtractor()
        extractor.extract_symbols(lines)
        
        sym = extractor.get_symbol_by_name("bar")
        assert sym is None


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_lines(self):
        """Test with empty lines list."""
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols([])
        
        assert symbols == []
    
    def test_only_whitespace(self):
        """Test with only whitespace lines."""
        lines = ["   ", "\t", "  \t  "]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        assert symbols == []
    
    def test_complex_sagemath_code(self):
        """Test with complex SageMath code."""
        lines = [
            "from sage.all import *",
            "",
            "R.<x, y> = PolynomialRing(QQ, order='degrevlex')",
            "I = R.ideal([x^2 - y, y^2 - x])",
            "gb = I.groebner_basis()",
            "",
            "def my_algo(f, g):",
            '    """Compute something."""',
            "    return f * g",
            "",
            "result = my_algo(x, y)",
        ]
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(lines)
        
        names = [s.name for s in symbols]
        assert "R" in names
        assert "x" in names
        assert "y" in names
        assert "I" in names
        assert "gb" in names
        assert "my_algo" in names
        assert "result" in names
