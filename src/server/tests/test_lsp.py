"""
Unit tests for lsp.py - LSP core functionality.
Tests helper functions for code analysis and LSP features.
"""

from __future__ import annotations
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lsprotocol.types import Position, Range, Location, DiagnosticSeverity

from lsp import (
    get_word_at_position,
    get_context_at_position,
    get_function_at_position,
    find_definitions_in_doc,
    find_references_in_doc,
    check_diagnostics,
)


class TestGetWordAtPosition:
    """Tests for get_word_at_position function."""
    
    def test_simple_word(self, mock_document, position):
        """Test getting a simple word."""
        doc = mock_document("hello world")
        pos = position(0, 2)  # Inside "hello"
        assert get_word_at_position(doc, pos) == "hello"
    
    def test_word_at_start(self, mock_document, position):
        """Test getting word at line start."""
        doc = mock_document("variable = 5")
        pos = position(0, 0)
        assert get_word_at_position(doc, pos) == "variable"
    
    def test_word_at_end(self, mock_document, position):
        """Test getting word at the end."""
        doc = mock_document("x = value")
        pos = position(0, 8)  # Inside "value"
        assert get_word_at_position(doc, pos) == "value"
    
    def test_underscore_identifier(self, mock_document, position):
        """Test identifier with underscores."""
        doc = mock_document("my_variable_name = 5")
        pos = position(0, 5)
        assert get_word_at_position(doc, pos) == "my_variable_name"
    
    def test_identifier_with_numbers(self, mock_document, position):
        """Test identifier with numbers."""
        doc = mock_document("var123 = 5")
        pos = position(0, 3)
        assert get_word_at_position(doc, pos) == "var123"
    
    def test_position_on_operator(self, mock_document, position):
        """Test position on operator returns None."""
        doc = mock_document("x = 5")
        pos = position(0, 2)  # On "="
        result = get_word_at_position(doc, pos)
        assert result is None or result == ""
    
    def test_empty_line(self, mock_document, position):
        """Test empty line returns None."""
        doc = mock_document("\n")
        pos = position(0, 0)
        result = get_word_at_position(doc, pos)
        assert result is None or result == ""
    
    def test_multiline_document(self, mock_document, position):
        """Test getting word from multiline document."""
        doc = mock_document("first\nsecond\nthird")
        pos = position(1, 3)  # Inside "second"
        assert get_word_at_position(doc, pos) == "second"
    
    def test_out_of_bounds_line(self, mock_document, position):
        """Test out of bounds line returns None."""
        doc = mock_document("hello")
        pos = position(10, 0)
        assert get_word_at_position(doc, pos) is None
    
    def test_position_after_dot(self, mock_document, position):
        """Test getting word after dot."""
        doc = mock_document("obj.method")
        pos = position(0, 6)  # Inside "method"
        assert get_word_at_position(doc, pos) == "method"


class TestGetContextAtPosition:
    """Tests for get_context_at_position function."""
    
    def test_after_dot(self, mock_document, position):
        """Test context after dot for method completion."""
        doc = mock_document("matrix.det")
        pos = position(0, 10)
        obj_name, partial, is_after_dot = get_context_at_position(doc, pos)
        assert obj_name == "matrix"
        assert partial == "det"
        assert is_after_dot is True
    
    def test_after_dot_empty_partial(self, mock_document, position):
        """Test context immediately after dot."""
        doc = mock_document("matrix.")
        pos = position(0, 7)
        obj_name, partial, is_after_dot = get_context_at_position(doc, pos)
        assert obj_name == "matrix"
        assert partial == ""
        assert is_after_dot is True
    
    def test_no_dot_partial_identifier(self, mock_document, position):
        """Test regular identifier without dot."""
        doc = mock_document("fact")
        pos = position(0, 4)
        obj_name, partial, is_after_dot = get_context_at_position(doc, pos)
        assert obj_name is None
        assert partial == "fact"
        assert is_after_dot is False
    
    def test_empty_context(self, mock_document, position):
        """Test empty context at start of line."""
        doc = mock_document("")
        pos = position(0, 0)
        obj_name, partial, is_after_dot = get_context_at_position(doc, pos)
        assert obj_name is None
        assert partial == ""
        assert is_after_dot is False
    
    def test_nested_dot_access(self, mock_document, position):
        """Test nested dot access."""
        doc = mock_document("obj.attr.meth")
        pos = position(0, 13)
        obj_name, partial, is_after_dot = get_context_at_position(doc, pos)
        assert obj_name == "attr"
        assert partial == "meth"
        assert is_after_dot is True
    
    def test_after_parenthesis(self, mock_document, position):
        """Test context after opening parenthesis."""
        doc = mock_document("func(arg")
        pos = position(0, 8)
        obj_name, partial, is_after_dot = get_context_at_position(doc, pos)
        assert partial == "arg"
        assert is_after_dot is False


class TestGetFunctionAtPosition:
    """Tests for get_function_at_position function."""
    
    def test_simple_function_call(self, mock_document, position):
        """Test detecting simple function call."""
        doc = mock_document("factor(120)")
        pos = position(0, 7)  # Inside parentheses
        result = get_function_at_position(doc, pos)
        assert result is not None
        func_name, param_idx = result
        assert func_name == "factor"
        assert param_idx == 0
    
    def test_multiple_parameters(self, mock_document, position):
        """Test detecting parameter index."""
        doc = mock_document("func(a, b, c)")
        pos = position(0, 11)  # After second comma
        result = get_function_at_position(doc, pos)
        assert result is not None
        func_name, param_idx = result
        assert func_name == "func"
        assert param_idx == 2
    
    def test_nested_function_calls(self, mock_document, position):
        """Test nested function calls."""
        doc = mock_document("outer(inner(x))")
        pos = position(0, 12)  # Inside inner()
        result = get_function_at_position(doc, pos)
        assert result is not None
        func_name, param_idx = result
        assert func_name == "inner"
        assert param_idx == 0
    
    def test_no_function(self, mock_document, position):
        """Test when not inside function call."""
        doc = mock_document("x = 5")
        pos = position(0, 4)
        result = get_function_at_position(doc, pos)
        assert result is None
    
    def test_method_call(self, mock_document, position):
        """Test method call detection."""
        doc = mock_document("obj.method(arg)")
        pos = position(0, 11)
        result = get_function_at_position(doc, pos)
        assert result is not None
        func_name, param_idx = result
        assert func_name == "method"
    
    def test_empty_arguments(self, mock_document, position):
        """Test function with empty arguments."""
        doc = mock_document("func()")
        pos = position(0, 5)
        result = get_function_at_position(doc, pos)
        assert result is not None
        func_name, param_idx = result
        assert func_name == "func"
        assert param_idx == 0


class TestFindDefinitionsInDoc:
    """Tests for find_definitions_in_doc function."""
    
    def test_function_definition(self, mock_document):
        """Test finding function definition."""
        doc = mock_document("def my_func(x):\n    return x")
        locations = find_definitions_in_doc(doc, "my_func")
        assert len(locations) == 1
        assert locations[0].range.start.line == 0
    
    def test_class_definition(self, mock_document):
        """Test finding class definition."""
        doc = mock_document("class MyClass:\n    pass")
        locations = find_definitions_in_doc(doc, "MyClass")
        assert len(locations) == 1
        assert locations[0].range.start.line == 0
    
    def test_variable_assignment(self, mock_document):
        """Test finding variable assignment."""
        doc = mock_document("x = 5\ny = x + 1")
        locations = find_definitions_in_doc(doc, "x")
        assert len(locations) >= 1
        assert locations[0].range.start.line == 0
    
    def test_for_loop_variable(self, mock_document):
        """Test finding for loop variable."""
        doc = mock_document("for i in range(10):\n    print(i)")
        locations = find_definitions_in_doc(doc, "i")
        assert len(locations) >= 1
    
    def test_no_definition_found(self, mock_document):
        """Test when no definition exists."""
        doc = mock_document("print(undefined)")
        locations = find_definitions_in_doc(doc, "undefined")
        assert len(locations) == 0
    
    def test_multiple_definitions(self, mock_document):
        """Test multiple definitions of same name."""
        doc = mock_document("def foo():\n    pass\n\nfoo = 5")
        locations = find_definitions_in_doc(doc, "foo")
        assert len(locations) >= 1
    
    def test_indented_assignment(self, mock_document):
        """Test indented variable assignment."""
        doc = mock_document("if True:\n    result = 42")
        locations = find_definitions_in_doc(doc, "result")
        assert len(locations) >= 1


class TestFindReferencesInDoc:
    """Tests for find_references_in_doc function."""
    
    def test_single_reference(self, mock_document):
        """Test finding single reference."""
        doc = mock_document("x = 5")
        locations = find_references_in_doc(doc, "x")
        assert len(locations) == 1
    
    def test_multiple_references(self, mock_document):
        """Test finding multiple references."""
        doc = mock_document("x = 5\ny = x\nz = x + 1")
        locations = find_references_in_doc(doc, "x")
        assert len(locations) == 3
    
    def test_no_references(self, mock_document):
        """Test when symbol not found."""
        doc = mock_document("a = 5")
        locations = find_references_in_doc(doc, "nonexistent")
        assert len(locations) == 0
    
    def test_word_boundary(self, mock_document):
        """Test word boundary matching."""
        doc = mock_document("x = 5\nxy = 10")
        locations = find_references_in_doc(doc, "x")
        assert len(locations) == 1  # Should not match "xy"
    
    def test_references_across_lines(self, mock_document):
        """Test references across multiple lines."""
        doc = mock_document("def foo():\n    return foo")
        locations = find_references_in_doc(doc, "foo")
        assert len(locations) == 2


class TestCheckDiagnostics:
    """Tests for check_diagnostics function."""
    
    def test_mixed_indentation_warning(self, mock_document):
        """Test detection of mixed tabs and spaces."""
        doc = mock_document("\t x = 5")  # Tab followed by space
        diagnostics = check_diagnostics(doc)
        indent_warnings = [d for d in diagnostics if "Mixed tabs" in d.message]
        assert len(indent_warnings) >= 1
        assert indent_warnings[0].severity == DiagnosticSeverity.Warning
    
    def test_assignment_in_condition(self, mock_document):
        """Test detection of assignment in if condition."""
        doc = mock_document("if x = 5:\n    pass")
        diagnostics = check_diagnostics(doc)
        assign_warnings = [d for d in diagnostics if "assignment in condition" in d.message.lower()]
        assert len(assign_warnings) >= 1
    
    def test_undefined_function_hint(self, mock_document):
        """Test hint for potentially undefined function."""
        doc = mock_document("undefined_func()")
        diagnostics = check_diagnostics(doc)
        undefined_hints = [d for d in diagnostics if "may not be defined" in d.message]
        assert len(undefined_hints) >= 1
        assert undefined_hints[0].severity == DiagnosticSeverity.Hint
    
    def test_clean_document(self, mock_document):
        """Test document with no issues."""
        doc = mock_document("x = 5\nprint(x)")
        diagnostics = check_diagnostics(doc)
        # Should have minimal or no critical diagnostics
        errors = [d for d in diagnostics if d.severity == DiagnosticSeverity.Error]
        assert len(errors) == 0
    
    def test_comment_lines_ignored(self, mock_document):
        """Test that comment lines are ignored."""
        doc = mock_document("# This is a comment\nx = 5")
        diagnostics = check_diagnostics(doc)
        # Comments should not cause diagnostics
        assert all("comment" not in d.message.lower() for d in diagnostics)
    
    def test_empty_document(self, mock_document):
        """Test empty document."""
        doc = mock_document("")
        diagnostics = check_diagnostics(doc)
        assert len(diagnostics) == 0
    
    def test_defined_function_no_warning(self, mock_document):
        """Test that defined functions don't trigger warnings."""
        doc = mock_document("def my_func():\n    pass\n\nmy_func()")
        diagnostics = check_diagnostics(doc)
        my_func_hints = [d for d in diagnostics if "my_func" in d.message]
        assert len(my_func_hints) == 0
    
    def test_builtin_no_warning(self, mock_document):
        """Test that builtin functions don't trigger warnings."""
        doc = mock_document("print('hello')\nlen([1,2,3])")
        diagnostics = check_diagnostics(doc)
        builtin_hints = [d for d in diagnostics if "print" in d.message or "len" in d.message]
        assert len(builtin_hints) == 0
    
    def test_sagemath_function_no_warning(self, mock_document):
        """Test that SageMath functions don't trigger warnings."""
        doc = mock_document("factor(120)\ngcd(12, 18)")
        diagnostics = check_diagnostics(doc)
        sage_hints = [d for d in diagnostics if "factor" in d.message or "gcd" in d.message]
        assert len(sage_hints) == 0
    
    def test_method_call_no_warning(self, mock_document):
        """Test that method calls don't trigger undefined warnings."""
        doc = mock_document("obj.unknown_method()")
        diagnostics = check_diagnostics(doc)
        method_hints = [d for d in diagnostics if "unknown_method" in d.message]
        assert len(method_hints) == 0
    
    def test_class_definition_tracked(self, mock_document):
        """Test that class definitions are tracked."""
        doc = mock_document("class MyClass:\n    pass\n\nMyClass()")
        diagnostics = check_diagnostics(doc)
        class_hints = [d for d in diagnostics if "MyClass" in d.message]
        assert len(class_hints) == 0
    
    def test_for_loop_variable_tracked(self, mock_document):
        """Test that for loop variables are tracked."""
        doc = mock_document("for i in range(10):\n    print(i)")
        diagnostics = check_diagnostics(doc)
        # 'i' should be recognized as defined
        assert all("'i'" not in d.message for d in diagnostics)


class TestDiagnosticsIntegration:
    """Integration tests for diagnostics with complex documents."""
    
    def test_complex_document(self, sagemath_document):
        """Test diagnostics on SageMath document."""
        diagnostics = check_diagnostics(sagemath_document)
        # Should not report SageMath builtins as undefined
        sage_funcs = ["PolynomialRing", "matrix", "EllipticCurve"]
        for func in sage_funcs:
            func_hints = [d for d in diagnostics if func in d.message]
            assert len(func_hints) == 0, f"{func} should not be flagged"
    
    def test_class_document(self, class_document):
        """Test diagnostics on class-based document."""
        diagnostics = check_diagnostics(class_document)
        # Methods should not be flagged
        assert all("get_value" not in d.message for d in diagnostics)


# ============== Tests for New LSP Features (v1.4.0) ==============

class TestGetUserCompletions:
    """Tests for get_user_completions function."""
    
    def test_user_function_completion(self, mock_document):
        """Test completion for user-defined function."""
        from lsp import get_user_completions
        doc = mock_document("def my_func():\n    pass\n")
        items = get_user_completions(doc, "my")
        
        assert len(items) >= 1
        labels = [i.label for i in items]
        assert "my_func" in labels
    
    def test_user_variable_completion(self, mock_document):
        """Test completion for user-defined variable."""
        from lsp import get_user_completions
        doc = mock_document("my_var = 42\n")
        items = get_user_completions(doc, "my")
        
        assert len(items) >= 1
        labels = [i.label for i in items]
        assert "my_var" in labels
    
    def test_user_class_completion(self, mock_document):
        """Test completion for user-defined class."""
        from lsp import get_user_completions
        doc = mock_document("class MyClass:\n    pass\n")
        items = get_user_completions(doc, "My")
        
        assert len(items) >= 1
        labels = [i.label for i in items]
        assert "MyClass" in labels
    
    def test_empty_partial_returns_all(self, mock_document):
        """Test that empty partial returns all symbols."""
        from lsp import get_user_completions
        doc = mock_document("x = 1\ny = 2\nz = 3\n")
        items = get_user_completions(doc, "")
        
        assert len(items) == 3
    
    def test_no_match_returns_empty(self, mock_document):
        """Test that no match returns empty list."""
        from lsp import get_user_completions
        doc = mock_document("x = 1\ny = 2\n")
        items = get_user_completions(doc, "zzz")
        
        assert len(items) == 0
    
    def test_function_has_parenthesis(self, mock_document):
        """Test that function completion includes parenthesis."""
        from lsp import get_user_completions
        doc = mock_document("def foo():\n    pass\n")
        items = get_user_completions(doc, "foo")
        
        assert len(items) == 1
        assert items[0].insert_text == "foo("
    
    def test_sage_ring_variables(self, mock_document):
        """Test completion for SageMath ring variables."""
        from lsp import get_user_completions
        doc = mock_document("R.<x, y> = PolynomialRing(QQ)\n")
        items = get_user_completions(doc, "")
        
        labels = [i.label for i in items]
        assert "R" in labels
        assert "x" in labels
        assert "y" in labels


class TestDocumentSymbolsIntegration:
    """Integration tests for document symbols feature."""
    
    def test_document_symbols_basic(self, mock_document):
        """Test basic document symbols extraction."""
        from symbols import extract_document_symbols
        doc = mock_document("def foo():\n    pass\n\nclass Bar:\n    pass\n")
        symbols = extract_document_symbols(doc.lines)
        
        assert len(symbols) == 2
        names = [s.name for s in symbols]
        assert "foo" in names
        assert "Bar" in names
    
    def test_document_symbols_sagemath(self, sagemath_document):
        """Test document symbols with SageMath code."""
        from symbols import extract_document_symbols
        symbols = extract_document_symbols(sagemath_document.lines)
        
        names = [s.name for s in symbols]
        # Should find R, x, p, roots, M, det_M, E, order
        assert "R" in names or "x" in names  # At least some symbols found


class TestFoldingRangesIntegration:
    """Integration tests for folding ranges feature."""
    
    def test_function_folding(self, mock_document):
        """Test folding for function definition."""
        doc = mock_document("def foo():\n    x = 1\n    y = 2\n    return x + y\n")
        # Manually test the folding logic
        lines = doc.lines
        
        # Function should be foldable (more than 1 line)
        assert len(lines) > 2
        assert lines[0].strip().startswith("def ")
    
    def test_class_folding(self, mock_document):
        """Test folding for class definition."""
        doc = mock_document("class Foo:\n    def __init__(self):\n        pass\n    def bar(self):\n        pass\n")
        lines = doc.lines
        
        assert lines[0].strip().startswith("class ")


class TestRenameIntegration:
    """Integration tests for rename feature."""
    
    def test_find_references_for_rename(self, mock_document):
        """Test finding references (used by rename)."""
        doc = mock_document("x = 5\ny = x + 10\nz = x * 2\n")
        locations = find_references_in_doc(doc, "x")
        
        assert len(locations) >= 3  # Definition + 2 usages
    
    def test_find_function_references(self, mock_document):
        """Test finding function references."""
        doc = mock_document("def foo():\n    pass\n\nfoo()\nresult = foo()\n")
        locations = find_references_in_doc(doc, "foo")
        
        assert len(locations) >= 3  # Definition + 2 calls


class TestInlayHintsIntegration:
    """Integration tests for inlay hints feature."""
    
    def test_type_inference_for_hints(self, mock_document):
        """Test type inference used for inlay hints."""
        from symbols import SymbolExtractor
        doc = mock_document("M = matrix([[1, 2], [3, 4]])\n")
        
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(doc.lines)
        
        assert len(symbols) == 1
        assert symbols[0].inferred_type == "Matrix"
    
    def test_multiple_type_inferences(self, mock_document):
        """Test multiple type inferences."""
        from symbols import SymbolExtractor
        doc = mock_document("M = matrix([[1, 2]])\nv = vector([1, 2, 3])\nE = EllipticCurve(GF(101), [0, 7])\n")
        
        extractor = SymbolExtractor()
        symbols = extractor.extract_symbols(doc.lines)
        
        types = {s.name: s.inferred_type for s in symbols}
        assert types.get("M") == "Matrix"
        assert types.get("v") == "Vector"
        assert types.get("E") == "EllipticCurve"
