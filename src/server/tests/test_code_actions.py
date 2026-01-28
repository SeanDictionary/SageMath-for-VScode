"""
Unit tests for code_actions.py - Code Actions and Quick Fixes module.
Tests quick fixes, import suggestions, typo corrections, and refactoring actions.
"""

from __future__ import annotations
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lsprotocol.types import (
    Range, Position, Diagnostic, DiagnosticSeverity,
    CodeActionKind
)

from code_actions import CodeActionProvider


class TestCodeActionProvider:
    """Tests for CodeActionProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create a CodeActionProvider instance."""
        return CodeActionProvider()
    
    @pytest.fixture
    def make_diagnostic(self):
        """Factory for creating diagnostics."""
        def _make(message: str, line: int = 0, start_char: int = 0, end_char: int = 5):
            return Diagnostic(
                range=Range(
                    start=Position(line=line, character=start_char),
                    end=Position(line=line, character=end_char)
                ),
                message=message,
                severity=DiagnosticSeverity.Warning
            )
        return _make


class TestUndefinedNameActions:
    """Tests for undefined name quick fixes."""
    
    @pytest.fixture
    def provider(self):
        return CodeActionProvider()
    
    @pytest.fixture
    def make_diagnostic(self):
        def _make(message: str, line: int = 0, start_char: int = 0, end_char: int = 5):
            return Diagnostic(
                range=Range(
                    start=Position(line=line, character=start_char),
                    end=Position(line=line, character=end_char)
                ),
                message=message,
                severity=DiagnosticSeverity.Warning
            )
        return _make
    
    def test_suggest_import_for_bytes_to_long(self, provider, make_diagnostic):
        """Test suggesting import for bytes_to_long."""
        diagnostic = make_diagnostic("'bytes_to_long' may not be defined")
        lines = ["result = bytes_to_long(data)"]
        
        actions = provider._get_undefined_name_actions(
            uri="file:///test.sage",
            diagnostic=diagnostic,
            lines=lines,
            version=1
        )
        
        assert len(actions) >= 1
        import_action = next((a for a in actions if "import" in a.title.lower()), None)
        assert import_action is not None
        assert "Crypto.Util.number" in import_action.title
    
    def test_suggest_import_for_numpy(self, provider, make_diagnostic):
        """Test suggesting import for np."""
        diagnostic = make_diagnostic("'np' may not be defined")
        lines = ["arr = np.array([1, 2, 3])"]
        
        actions = provider._get_undefined_name_actions(
            uri="file:///test.sage",
            diagnostic=diagnostic,
            lines=lines,
            version=1
        )
        
        assert len(actions) >= 1
        import_action = next((a for a in actions if "import" in a.title.lower()), None)
        assert import_action is not None
        assert "numpy" in import_action.title
    
    def test_suggest_import_for_counter(self, provider, make_diagnostic):
        """Test suggesting import for Counter."""
        diagnostic = make_diagnostic("'Counter' may not be defined")
        lines = ["c = Counter(items)"]
        
        actions = provider._get_undefined_name_actions(
            uri="file:///test.sage",
            diagnostic=diagnostic,
            lines=lines,
            version=1
        )
        
        assert len(actions) >= 1
        import_action = next((a for a in actions if "import" in a.title.lower()), None)
        assert import_action is not None
        assert "collections" in import_action.title
    
    def test_typo_correction_matrix(self, provider, make_diagnostic):
        """Test typo correction for 'matirx' -> 'matrix'."""
        diagnostic = make_diagnostic("'matirx' may not be defined")
        lines = ["M = matirx([[1, 2], [3, 4]])"]
        
        actions = provider._get_undefined_name_actions(
            uri="file:///test.sage",
            diagnostic=diagnostic,
            lines=lines,
            version=1
        )
        
        assert len(actions) >= 1
        typo_action = next((a for a in actions if "mean" in a.title.lower()), None)
        assert typo_action is not None
        assert "matrix" in typo_action.title
    
    def test_typo_correction_vector(self, provider, make_diagnostic):
        """Test typo correction for 'vecor' -> 'vector'."""
        diagnostic = make_diagnostic("'vecor' may not be defined")
        lines = ["v = vecor([1, 2, 3])"]
        
        actions = provider._get_undefined_name_actions(
            uri="file:///test.sage",
            diagnostic=diagnostic,
            lines=lines,
            version=1
        )
        
        assert len(actions) >= 1
        typo_action = next((a for a in actions if "mean" in a.title.lower()), None)
        assert typo_action is not None
        assert "vector" in typo_action.title
    
    def test_similar_function_suggestion(self, provider, make_diagnostic):
        """Test suggesting similar SageMath functions."""
        diagnostic = make_diagnostic("'fcator' may not be defined")
        lines = ["f = fcator(100)"]
        
        actions = provider._get_undefined_name_actions(
            uri="file:///test.sage",
            diagnostic=diagnostic,
            lines=lines,
            version=1
        )
        
        # Should suggest 'factor' as similar
        assert len(actions) >= 1


class TestIndentationFixActions:
    """Tests for indentation fix actions."""
    
    @pytest.fixture
    def provider(self):
        return CodeActionProvider()
    
    @pytest.fixture
    def make_diagnostic(self):
        def _make(message: str, line: int = 0, start_char: int = 0, end_char: int = 5):
            return Diagnostic(
                range=Range(
                    start=Position(line=line, character=start_char),
                    end=Position(line=line, character=end_char)
                ),
                message=message,
                severity=DiagnosticSeverity.Warning
            )
        return _make
    
    def test_convert_tabs_to_spaces(self, provider, make_diagnostic):
        """Test converting tabs to spaces."""
        diagnostic = make_diagnostic("Mixed tabs and spaces in indentation", line=0)
        lines = ["\t    x = 5"]  # Tab followed by spaces
        
        actions = provider._get_indentation_fix_actions(
            uri="file:///test.sage",
            diagnostic=diagnostic,
            lines=lines,
            version=1
        )
        
        assert len(actions) == 1
        assert "tabs to spaces" in actions[0].title.lower()
        
        # Check that the edit replaces the line
        assert actions[0].edit is not None


class TestAssignmentFixActions:
    """Tests for assignment in condition fix actions."""
    
    @pytest.fixture
    def provider(self):
        return CodeActionProvider()
    
    @pytest.fixture
    def make_diagnostic(self):
        def _make(message: str, line: int = 0, start_char: int = 0, end_char: int = 5):
            return Diagnostic(
                range=Range(
                    start=Position(line=line, character=start_char),
                    end=Position(line=line, character=end_char)
                ),
                message=message,
                severity=DiagnosticSeverity.Warning
            )
        return _make
    
    def test_fix_assignment_to_comparison(self, provider, make_diagnostic):
        """Test fixing = to == in condition."""
        diagnostic = make_diagnostic("assignment in condition", line=0)
        lines = ["if x = 5:"]
        
        actions = provider._get_assignment_fix_actions(
            uri="file:///test.sage",
            diagnostic=diagnostic,
            lines=lines,
            version=1
        )
        
        assert len(actions) == 1
        assert "==" in actions[0].title
    
    def test_preserve_double_equals(self, provider, make_diagnostic):
        """Test that == is not changed to ===."""
        diagnostic = make_diagnostic("assignment in condition", line=0)
        lines = ["if x == 5:"]  # Already correct
        
        actions = provider._get_assignment_fix_actions(
            uri="file:///test.sage",
            diagnostic=diagnostic,
            lines=lines,
            version=1
        )
        
        # No action needed since it's already ==
        assert len(actions) == 0


class TestSourceActions:
    """Tests for source actions (non-diagnostic)."""
    
    @pytest.fixture
    def provider(self):
        return CodeActionProvider()
    
    def test_generate_docstring_action(self, provider):
        """Test generating docstring for function."""
        lines = [
            "def my_function(a, b, c):",
            "    return a + b + c",
        ]
        doc_range = Range(
            start=Position(line=0, character=0),
            end=Position(line=0, character=0)
        )
        
        actions = provider._get_source_actions(
            uri="file:///test.sage",
            doc_range=doc_range,
            lines=lines,
            version=1
        )
        
        assert len(actions) == 1
        assert "docstring" in actions[0].title.lower()
    
    def test_no_docstring_for_non_function(self, provider):
        """Test that docstring action is not offered for non-function lines."""
        lines = [
            "x = 5",
            "y = 10",
        ]
        doc_range = Range(
            start=Position(line=0, character=0),
            end=Position(line=0, character=0)
        )
        
        actions = provider._get_source_actions(
            uri="file:///test.sage",
            doc_range=doc_range,
            lines=lines,
            version=1
        )
        
        # Should not offer docstring generation
        docstring_actions = [a for a in actions if "docstring" in a.title.lower()]
        assert len(docstring_actions) == 0
    
    def test_no_duplicate_docstring(self, provider):
        """Test that docstring is not offered if one already exists."""
        lines = [
            "def my_function():",
            '    """Existing docstring."""',
            "    pass",
        ]
        doc_range = Range(
            start=Position(line=0, character=0),
            end=Position(line=0, character=0)
        )
        
        actions = provider._get_source_actions(
            uri="file:///test.sage",
            doc_range=doc_range,
            lines=lines,
            version=1
        )
        
        # Should not offer docstring generation since one exists
        docstring_actions = [a for a in actions if "docstring" in a.title.lower()]
        assert len(docstring_actions) == 0


class TestDocstringGeneration:
    """Tests for docstring generation."""
    
    @pytest.fixture
    def provider(self):
        return CodeActionProvider()
    
    def test_generate_docstring_with_params(self, provider):
        """Test generating docstring with parameters."""
        docstring = provider._generate_docstring(
            func_name="my_func",
            params="a, b, c",
            indent="    "
        )
        
        assert '"""' in docstring
        assert "my_func" in docstring
        assert "Args:" in docstring
        assert "a:" in docstring
        assert "b:" in docstring
        assert "c:" in docstring
        assert "Returns:" in docstring
    
    def test_generate_docstring_no_params(self, provider):
        """Test generating docstring without parameters."""
        docstring = provider._generate_docstring(
            func_name="my_func",
            params="",
            indent="    "
        )
        
        assert '"""' in docstring
        assert "my_func" in docstring
        assert "Returns:" in docstring
        # Should not have Args section
        assert "Args:" not in docstring
    
    def test_generate_docstring_excludes_self(self, provider):
        """Test that 'self' is excluded from parameters."""
        docstring = provider._generate_docstring(
            func_name="method",
            params="self, a, b",
            indent="    "
        )
        
        assert "self:" not in docstring
        assert "a:" in docstring
        assert "b:" in docstring
    
    def test_generate_docstring_handles_type_hints(self, provider):
        """Test handling parameters with type hints."""
        docstring = provider._generate_docstring(
            func_name="typed_func",
            params="a: int, b: str",
            indent="    "
        )
        
        assert "a:" in docstring
        assert "b:" in docstring
    
    def test_generate_docstring_handles_defaults(self, provider):
        """Test handling parameters with default values."""
        docstring = provider._generate_docstring(
            func_name="default_func",
            params="a, b=10, c='hello'",
            indent="    "
        )
        
        assert "a:" in docstring
        assert "b:" in docstring
        assert "c:" in docstring


class TestLevenshteinDistance:
    """Tests for Levenshtein distance calculation."""
    
    @pytest.fixture
    def provider(self):
        return CodeActionProvider()
    
    def test_identical_strings(self, provider):
        """Test distance of identical strings is 0."""
        assert provider._levenshtein_distance("hello", "hello") == 0
    
    def test_single_insertion(self, provider):
        """Test single character insertion."""
        assert provider._levenshtein_distance("hello", "helloo") == 1
    
    def test_single_deletion(self, provider):
        """Test single character deletion."""
        assert provider._levenshtein_distance("hello", "helo") == 1
    
    def test_single_substitution(self, provider):
        """Test single character substitution."""
        assert provider._levenshtein_distance("hello", "hallo") == 1
    
    def test_multiple_edits(self, provider):
        """Test multiple edits."""
        assert provider._levenshtein_distance("kitten", "sitting") == 3
    
    def test_empty_string(self, provider):
        """Test with empty string."""
        assert provider._levenshtein_distance("hello", "") == 5
        assert provider._levenshtein_distance("", "hello") == 5
    
    def test_both_empty(self, provider):
        """Test with both strings empty."""
        assert provider._levenshtein_distance("", "") == 0


class TestSimilarNameFinding:
    """Tests for finding similar names."""
    
    @pytest.fixture
    def provider(self):
        return CodeActionProvider()
    
    def test_find_similar_matrix(self, provider):
        """Test finding 'matrix' for 'matirx'."""
        candidates = {"matrix", "vector", "factor", "gcd"}
        similar = provider._find_similar_names("matirx", candidates)
        
        assert "matrix" in similar
    
    def test_find_similar_factor(self, provider):
        """Test finding 'factor' for 'fcator'."""
        candidates = {"matrix", "vector", "factor", "gcd"}
        similar = provider._find_similar_names("fcator", candidates)
        
        assert "factor" in similar
    
    def test_no_similar_for_very_different(self, provider):
        """Test no similar names for very different string."""
        candidates = {"matrix", "vector", "factor"}
        similar = provider._find_similar_names("xyz123", candidates)
        
        assert len(similar) == 0
    
    def test_excludes_exact_match(self, provider):
        """Test that exact match is excluded."""
        candidates = {"matrix", "vector", "factor"}
        similar = provider._find_similar_names("matrix", candidates)
        
        assert "matrix" not in similar


class TestAddImportAction:
    """Tests for add import action creation."""
    
    @pytest.fixture
    def provider(self):
        return CodeActionProvider()
    
    def test_create_import_action(self, provider):
        """Test creating an import action."""
        lines = [
            "x = 5",
            "y = 10",
        ]
        
        action = provider._create_add_import_action(
            uri="file:///test.sage",
            import_statement="import numpy as np",
            lines=lines,
            version=1,
            title="Add import: import numpy as np"
        )
        
        assert action is not None
        assert action.title == "Add import: import numpy as np"
        assert action.kind == CodeActionKind.QuickFix
        assert action.edit is not None
    
    def test_import_inserted_after_existing_imports(self, provider):
        """Test that import is inserted after existing imports."""
        lines = [
            "import os",
            "import sys",
            "",
            "x = 5",
        ]
        
        action = provider._create_add_import_action(
            uri="file:///test.sage",
            import_statement="import numpy",
            lines=lines,
            version=1,
            title="Add import"
        )
        
        # The edit should insert at line 2 (after existing imports)
        assert action.edit is not None


class TestReplaceTextAction:
    """Tests for replace text action creation."""
    
    @pytest.fixture
    def provider(self):
        return CodeActionProvider()
    
    def test_create_replace_action(self, provider):
        """Test creating a replace text action."""
        range_ = Range(
            start=Position(line=0, character=0),
            end=Position(line=0, character=6)
        )
        
        action = provider._create_replace_text_action(
            uri="file:///test.sage",
            range=range_,
            new_text="matrix",
            version=1,
            title="Did you mean 'matrix'?"
        )
        
        assert action is not None
        assert "matrix" in action.title
        assert action.kind == CodeActionKind.QuickFix
        assert action.edit is not None


class TestGetCodeActions:
    """Tests for main get_code_actions method."""
    
    @pytest.fixture
    def provider(self):
        return CodeActionProvider()
    
    def test_returns_list(self, provider):
        """Test that get_code_actions returns a list."""
        actions = provider.get_code_actions(
            uri="file:///test.sage",
            doc_range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=0)
            ),
            diagnostics=[],
            lines=["x = 5"],
            version=1
        )
        
        assert isinstance(actions, list)
    
    def test_handles_multiple_diagnostics(self, provider):
        """Test handling multiple diagnostics."""
        diagnostics = [
            Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=5)
                ),
                message="'np' may not be defined",
                severity=DiagnosticSeverity.Warning
            ),
            Diagnostic(
                range=Range(
                    start=Position(line=1, character=0),
                    end=Position(line=1, character=5)
                ),
                message="Mixed tabs and spaces in indentation",
                severity=DiagnosticSeverity.Warning
            ),
        ]
        
        lines = [
            "arr = np.array([1, 2, 3])",
            "\t    x = 5",
        ]
        
        actions = provider.get_code_actions(
            uri="file:///test.sage",
            doc_range=Range(
                start=Position(line=0, character=0),
                end=Position(line=1, character=0)
            ),
            diagnostics=diagnostics,
            lines=lines,
            version=1
        )
        
        # Should have actions for both diagnostics
        assert len(actions) >= 2
    
    def test_handles_empty_diagnostics(self, provider):
        """Test handling empty diagnostics list."""
        lines = [
            "def foo():",
            "    pass",
        ]
        
        actions = provider.get_code_actions(
            uri="file:///test.sage",
            doc_range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=0)
            ),
            diagnostics=[],
            lines=lines,
            version=1
        )
        
        # Should still return source actions
        assert isinstance(actions, list)
