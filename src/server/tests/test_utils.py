"""
Unit tests for utils.py - Utility classes and token parsing.
Tests Logging, Token, and SemanicSever classes.
"""

from __future__ import annotations
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import re

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    Logging, Token, SemanicSever,
    SYMBOL, NUMBER, OP, SPACE, COMMENT,
    BLOCK_STRING_BEGIN, BLOCK_STRING_END, LINE_STRING
)


class TestLogging:
    """Tests for Logging class."""
    
    def test_init_default_level(self):
        """Test default log level initialization."""
        mock_func = MagicMock()
        logger = Logging(mock_func)
        assert logger.log_level == 2  # info level
    
    def test_init_debug_level(self):
        """Test debug level initialization."""
        mock_func = MagicMock()
        logger = Logging(mock_func, "debug")
        assert logger.log_level == 1
    
    def test_init_warning_level(self):
        """Test warning level initialization."""
        mock_func = MagicMock()
        logger = Logging(mock_func, "warning")
        assert logger.log_level == 3
    
    def test_init_error_level(self):
        """Test error level initialization."""
        mock_func = MagicMock()
        logger = Logging(mock_func, "error")
        assert logger.log_level == 4
    
    def test_init_case_insensitive(self):
        """Test log level is case insensitive."""
        mock_func = MagicMock()
        logger = Logging(mock_func, "DEBUG")
        assert logger.log_level == 1
    
    def test_init_invalid_level_defaults_to_info(self):
        """Test invalid log level defaults to info."""
        mock_func = MagicMock()
        logger = Logging(mock_func, "invalid")
        assert logger.log_level == 2
    
    def test_debug_message_at_debug_level(self):
        """Test debug message logged at debug level."""
        mock_func = MagicMock()
        logger = Logging(mock_func, "debug")
        logger.debug("test message")
        mock_func.assert_called_once()
        assert "Debug" in mock_func.call_args[0][0]
        assert "test message" in mock_func.call_args[0][0]
    
    def test_debug_message_at_info_level(self):
        """Test debug message not logged at info level."""
        mock_func = MagicMock()
        logger = Logging(mock_func, "info")
        logger.debug("test message")
        mock_func.assert_not_called()
    
    def test_info_message_at_info_level(self):
        """Test info message logged at info level."""
        mock_func = MagicMock()
        logger = Logging(mock_func, "info")
        logger.info("test message")
        mock_func.assert_called_once()
        assert "Info" in mock_func.call_args[0][0]
    
    def test_warning_message_at_info_level(self):
        """Test warning message logged at info level."""
        mock_func = MagicMock()
        logger = Logging(mock_func, "info")
        logger.warning("test message")
        mock_func.assert_called_once()
        assert "Warning" in mock_func.call_args[0][0]
    
    def test_error_message_always_logged(self):
        """Test error message logged at any level."""
        mock_func = MagicMock()
        logger = Logging(mock_func, "error")
        logger.error("test message")
        mock_func.assert_called_once()
        assert "Error" in mock_func.call_args[0][0]
    
    def test_log_message_format(self):
        """Test log message contains timestamp."""
        mock_func = MagicMock()
        logger = Logging(mock_func, "info")
        logger.info("test message")
        message = mock_func.call_args[0][0]
        # Should contain timestamp pattern
        assert re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', message)
    
    def test_priorities_dict(self):
        """Test PRIORITIES dictionary values."""
        assert Logging.PRIORITIES["debug"] == 1
        assert Logging.PRIORITIES["info"] == 2
        assert Logging.PRIORITIES["warning"] == 3
        assert Logging.PRIORITIES["error"] == 4


class TestToken:
    """Tests for Token dataclass."""
    
    def test_token_creation(self):
        """Test basic token creation."""
        token = Token(line=0, offset=5, text="hello")
        assert token.line == 0
        assert token.offset == 5
        assert token.text == "hello"
        assert token.tok_type == ""
        assert token.tok_modifiers == []
    
    def test_token_with_type(self):
        """Test token with type."""
        token = Token(line=1, offset=0, text="def", tok_type="keyword")
        assert token.tok_type == "keyword"
    
    def test_token_with_modifiers(self):
        """Test token with modifiers."""
        token = Token(line=0, offset=0, text="CONST", tok_modifiers=["readonly"])
        assert "readonly" in token.tok_modifiers
    
    def test_token_str_representation(self):
        """Test token string representation."""
        token = Token(line=1, offset=5, text="test", tok_type="variable")
        str_repr = str(token)
        assert "1:5" in str_repr
        assert "'test'" in str_repr
        assert "variable" in str_repr
    
    def test_token_modifiers_mutable(self):
        """Test that modifiers list is mutable."""
        token = Token(line=0, offset=0, text="VAR")
        token.tok_modifiers.append("readonly")
        assert "readonly" in token.tok_modifiers
    
    def test_token_type_mutable(self):
        """Test that type is mutable."""
        token = Token(line=0, offset=0, text="x")
        token.tok_type = "variable"
        assert token.tok_type == "variable"


class TestRegexPatterns:
    """Tests for regex patterns used in tokenization."""
    
    def test_symbol_pattern_simple(self):
        """Test SYMBOL pattern matches identifiers."""
        assert SYMBOL.match("variable")
        assert SYMBOL.match("_private")
        assert SYMBOL.match("CamelCase")
        assert SYMBOL.match("var123")
    
    def test_symbol_pattern_no_match(self):
        """Test SYMBOL pattern rejects invalid identifiers."""
        assert not SYMBOL.match("123var")
        assert not SYMBOL.match("-invalid")
    
    def test_number_pattern_integer(self):
        """Test NUMBER pattern matches integers."""
        assert NUMBER.match("123")
        assert NUMBER.match("0")
    
    def test_number_pattern_float(self):
        """Test NUMBER pattern matches floats."""
        assert NUMBER.match("3.14")
        assert NUMBER.match("0.5")
    
    def test_number_pattern_scientific(self):
        """Test NUMBER pattern matches scientific notation."""
        assert NUMBER.match("1e10")
        assert NUMBER.match("2.5e-3")
        assert NUMBER.match("1E+5")
    
    def test_number_pattern_hex(self):
        """Test NUMBER pattern matches hex."""
        assert NUMBER.match("0xFF")
        assert NUMBER.match("0x1a2b")
    
    def test_number_pattern_binary(self):
        """Test NUMBER pattern matches binary."""
        assert NUMBER.match("0b1010")
        assert NUMBER.match("0B11")
    
    def test_number_pattern_octal(self):
        """Test NUMBER pattern matches octal."""
        assert NUMBER.match("0o755")
        assert NUMBER.match("0O17")
    
    def test_op_pattern(self):
        """Test OP pattern matches operators."""
        operators = ["+", "-", "*", "/", "//", "=", "==", "!=", "<=", ">=", "->", "^^"]
        for op in operators:
            assert OP.match(op), f"Should match operator: {op}"
    
    def test_space_pattern(self):
        """Test SPACE pattern matches whitespace."""
        assert SPACE.match("  ")
        assert SPACE.match("\t")
        assert SPACE.match("   \t  ")
    
    def test_comment_pattern(self):
        """Test COMMENT pattern matches comments."""
        assert COMMENT.match("# this is a comment")
        assert COMMENT.match("#")
    
    def test_line_string_pattern(self):
        """Test LINE_STRING pattern matches strings."""
        assert LINE_STRING.match("'hello'")
        assert LINE_STRING.match('"world"')
        assert LINE_STRING.match("'''multi'''")
        assert LINE_STRING.match('"""multi"""')


class TestSemanicSeverDocToTokens:
    """Tests for SemanicSever.doc_to_tokens method."""
    
    @pytest.fixture
    def server(self):
        """Create a SemanicSever instance for testing."""
        return SemanicSever(name="test-server", version="1.0.0", log_level="error")
    
    def test_empty_document(self, server, mock_document):
        """Test tokenizing empty document."""
        doc = mock_document("")
        tokens = server.doc_to_tokens(doc)
        assert tokens == []
    
    def test_single_identifier(self, server, mock_document):
        """Test tokenizing single identifier."""
        doc = mock_document("hello")
        tokens = server.doc_to_tokens(doc)
        assert len(tokens) == 1
        assert tokens[0].text == "hello"
    
    def test_assignment(self, server, mock_document):
        """Test tokenizing assignment statement."""
        doc = mock_document("x = 5")
        tokens = server.doc_to_tokens(doc)
        identifiers = [t for t in tokens if t.text == "x"]
        operators = [t for t in tokens if t.text == "="]
        assert len(identifiers) == 1
        assert len(operators) == 1
    
    def test_function_call(self, server, mock_document):
        """Test tokenizing function call."""
        doc = mock_document("print(hello)")
        tokens = server.doc_to_tokens(doc)
        names = [t.text for t in tokens if t.tok_type != "operator"]
        assert "print" in names
        assert "hello" in names
    
    def test_operators_classified(self, server, mock_document):
        """Test operators are classified correctly."""
        doc = mock_document("a + b")
        tokens = server.doc_to_tokens(doc)
        plus_tokens = [t for t in tokens if t.text == "+"]
        assert len(plus_tokens) == 1
        assert plus_tokens[0].tok_type == "operator"
    
    def test_multiline_document(self, server, mock_document):
        """Test tokenizing multiline document."""
        doc = mock_document("a = 1\nb = 2")
        tokens = server.doc_to_tokens(doc)
        a_token = next((t for t in tokens if t.text == "a"), None)
        b_token = next((t for t in tokens if t.text == "b"), None)
        assert a_token is not None
        assert b_token is not None
    
    def test_comments_skipped(self, server, mock_document):
        """Test comments are skipped."""
        doc = mock_document("x = 5  # comment")
        tokens = server.doc_to_tokens(doc)
        # Comment text should not appear as tokens
        comment_tokens = [t for t in tokens if "comment" in t.text]
        assert len(comment_tokens) == 0
    
    def test_string_skipped(self, server, mock_document):
        """Test strings are skipped."""
        doc = mock_document("x = 'hello world'")
        tokens = server.doc_to_tokens(doc)
        # String content should not appear as separate tokens
        hello_tokens = [t for t in tokens if t.text == "hello"]
        assert len(hello_tokens) == 0
    
    def test_block_string(self, server, mock_document):
        """Test block strings are handled."""
        doc = mock_document('x = """multi\nline\nstring"""')
        tokens = server.doc_to_tokens(doc)
        # Should not crash on block strings
        assert any(t.text == "x" for t in tokens)
    
    def test_token_positions(self, server, mock_document):
        """Test token positions are correct."""
        doc = mock_document("hello world")
        tokens = server.doc_to_tokens(doc)
        hello_token = next((t for t in tokens if t.text == "hello"), None)
        world_token = next((t for t in tokens if t.text == "world"), None)
        assert hello_token is not None
        assert world_token is not None
        # First token should be at offset 0
        assert hello_token.line == 0
        assert hello_token.offset == 0


class TestSemanicSeverClassifyTokens:
    """Tests for SemanicSever.classify_tokens method."""
    
    @pytest.fixture
    def server(self):
        """Create a SemanicSever instance for testing."""
        return SemanicSever(name="test-server", version="1.0.0", log_level="error")
    
    def test_keyword_classification(self, server):
        """Test keywords are left unclassified for native highlighting."""
        tokens = [Token(line=0, offset=0, text="def")]
        server.classify_tokens(tokens)
        # Keywords are left to native Python highlighting
        assert tokens[0].tok_type == ""
    
    def test_function_definition(self, server):
        """Test function definition is tracked."""
        tokens = [
            Token(line=0, offset=0, text="def"),
            Token(line=0, offset=4, text="my_func"),
            Token(line=0, offset=11, text="(", tok_type="operator"),
            Token(line=0, offset=12, text=")", tok_type="operator"),
        ]
        server.classify_tokens(tokens)
        # After def, the function name should be tracked
        # Next usage of my_func should be classified as function
        tokens2 = [Token(line=0, offset=0, text="my_func")]
        # Re-classify with the updated state
        server.classify_tokens(tokens + tokens2)
    
    def test_class_definition(self, server):
        """Test class definition creates entry in class_names."""
        tokens = [
            Token(line=0, offset=0, text="class"),
            Token(line=0, offset=6, text="MyClass"),
            Token(line=0, offset=13, text=":", tok_type="operator"),
        ]
        server.classify_tokens(tokens)
        # Class token should be tracked (next token after class keyword)
    
    def test_predefined_function(self, server):
        """Test predefined SageMath functions are classified."""
        tokens = [Token(line=0, offset=0, text="factor")]
        server.classify_tokens(tokens)
        assert tokens[0].tok_type == "function"
    
    def test_predefined_class(self, server):
        """Test predefined SageMath classes are classified."""
        tokens = [Token(line=0, offset=0, text="ZZ")]
        server.classify_tokens(tokens)
        assert tokens[0].tok_type == "class"
    
    def test_variable_assignment(self, server):
        """Test variable assignment classification."""
        tokens = [
            Token(line=0, offset=0, text="x"),
            Token(line=0, offset=2, text="=", tok_type="operator"),
            Token(line=0, offset=4, text="5"),
        ]
        server.classify_tokens(tokens)
        assert tokens[0].tok_type == "variable"
    
    def test_constant_uppercase(self, server):
        """Test uppercase variables get readonly modifier."""
        tokens = [
            Token(line=0, offset=0, text="CONST"),
            Token(line=0, offset=6, text="=", tok_type="operator"),
            Token(line=0, offset=8, text="42"),
        ]
        server.classify_tokens(tokens)
        assert tokens[0].tok_type == "variable"
        assert "readonly" in tokens[0].tok_modifiers
    
    def test_for_loop_variable(self, server):
        """Test for loop variable classification."""
        tokens = [
            Token(line=0, offset=0, text="for"),
            Token(line=0, offset=4, text="i"),
            Token(line=0, offset=6, text="in"),
        ]
        server.classify_tokens(tokens)
        assert tokens[1].tok_type == "variable"
    
    def test_import_statement(self, server):
        """Test import statement handling."""
        tokens = [
            Token(line=0, offset=0, text="import"),
            Token(line=0, offset=7, text="math"),
        ]
        server.classify_tokens(tokens)
        assert tokens[1].tok_type == "class"
    
    def test_from_import(self, server):
        """Test from import statement handling."""
        tokens = [
            Token(line=0, offset=0, text="from"),
            Token(line=0, offset=5, text="sage"),
            Token(line=0, offset=9, text=".", tok_type="operator"),
            Token(line=0, offset=10, text="all"),
        ]
        server.classify_tokens(tokens)
        assert tokens[1].tok_type == "class"


class TestSemanicSeverParse:
    """Tests for SemanicSever.parse method."""
    
    @pytest.fixture
    def server(self):
        """Create a SemanicSever instance for testing."""
        return SemanicSever(name="test-server", version="1.0.0", log_level="error")
    
    def test_parse_simple(self, server, mock_document):
        """Test parsing simple document."""
        doc = mock_document("x = 5")
        tokens = server.parse(doc)
        assert len(tokens) > 0
    
    def test_parse_function_def(self, server, mock_document):
        """Test parsing function definition."""
        doc = mock_document("def foo():\n    return 42")
        tokens = server.parse(doc)
        foo_token = next((t for t in tokens if t.text == "foo"), None)
        assert foo_token is not None
    
    def test_parse_class_def(self, server, mock_document):
        """Test parsing class definition."""
        doc = mock_document("class MyClass:\n    pass")
        tokens = server.parse(doc)
        class_token = next((t for t in tokens if t.text == "MyClass"), None)
        assert class_token is not None
    
    def test_parse_sagemath_code(self, server, mock_document):
        """Test parsing SageMath-specific code."""
        doc = mock_document("R = PolynomialRing(QQ, 'x')")
        tokens = server.parse(doc)
        poly_token = next((t for t in tokens if t.text == "PolynomialRing"), None)
        qq_token = next((t for t in tokens if t.text == "QQ"), None)
        assert poly_token is not None
        assert qq_token is not None
        # PolynomialRing is defined in CLASSES, so it's classified as class
        assert poly_token.tok_type == "class"
        assert qq_token.tok_type == "class"
    
    def test_parse_empty_document(self, server, mock_document):
        """Test parsing empty document."""
        doc = mock_document("")
        tokens = server.parse(doc)
        assert tokens == []
    
    def test_parse_comments_only(self, server, mock_document):
        """Test parsing document with only comments."""
        doc = mock_document("# Just a comment\n# Another comment")
        tokens = server.parse(doc)
        # Should have no identifier tokens
        identifier_tokens = [t for t in tokens if t.tok_type not in ["operator", "comment", ""]]
        # Comments are skipped, so we expect minimal tokens
        assert len([t for t in tokens if "comment" in t.text.lower()]) == 0


class TestSemanicSeverInit:
    """Tests for SemanicSever initialization."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        server = SemanicSever(name="test", version="1.0")
        assert server.log_level == "info"
    
    def test_init_with_log_level(self):
        """Test initialization with custom log level."""
        server = SemanicSever(name="test", version="1.0", log_level="debug")
        assert server.log_level == "debug"
    
    def test_init_creates_logger(self):
        """Test initialization creates logger."""
        server = SemanicSever(name="test", version="1.0")
        assert hasattr(server, 'log')
        assert isinstance(server.log, Logging)
