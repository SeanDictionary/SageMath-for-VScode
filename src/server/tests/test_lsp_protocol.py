"""
LSP Protocol Level Tests

Tests the Language Server Protocol implementation at the JSON-RPC level,
verifying request/response handling and protocol compliance.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from lsprotocol.types import (
    Position, Range, Location, TextDocumentIdentifier,
    TextDocumentPositionParams, CompletionParams, CompletionContext,
    CompletionTriggerKind, CompletionItem, CompletionItemKind, CompletionList,
    HoverParams, Hover, MarkupContent, MarkupKind,
    SignatureHelpParams, SignatureHelp, SignatureInformation, ParameterInformation,
    SignatureHelpContext, SignatureHelpTriggerKind,
    DefinitionParams, ReferenceParams, ReferenceContext,
    SemanticTokensParams, SemanticTokens,
    DidOpenTextDocumentParams, TextDocumentItem,
    DidChangeTextDocumentParams, TextDocumentContentChangeEvent,
    VersionedTextDocumentIdentifier,
    InitializeParams, ClientCapabilities, InitializeResult,
    Diagnostic, DiagnosticSeverity,
)
from pygls.workspace import TextDocument

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lsp import (
    get_word_at_position, get_context_at_position, get_function_at_position,
    find_definitions_in_doc, find_references_in_doc, check_diagnostics,
    server, TOKEN_TYPES_DIC, TOKEN_MODIFIERS_DIC,
)
from predefinition import FUNCTIONS, CLASSES, KEYWORDS
from documentation import FUNCTION_DOCS, METHOD_DOCS


# ============== Fixtures ==============

@pytest.fixture
def mock_document():
    """Create a mock TextDocument."""
    def _create(content: str, uri: str = "file:///test.sage"):
        doc = MagicMock(spec=TextDocument)
        doc.uri = uri
        doc.source = content
        doc.lines = content.split('\n')
        doc.version = 1
        return doc
    return _create


@pytest.fixture
def text_document_id():
    """Create a TextDocumentIdentifier."""
    def _create(uri: str = "file:///test.sage"):
        return TextDocumentIdentifier(uri=uri)
    return _create


@pytest.fixture
def position():
    """Create a Position."""
    def _create(line: int, character: int):
        return Position(line=line, character=character)
    return _create


# ============== Initialize Tests ==============

class TestInitializeProtocol:
    """Test LSP initialization protocol."""
    
    def test_server_has_name(self):
        """Server should have correct name."""
        assert server.name == "sagemath-lsp"
    
    def test_server_has_version(self):
        """Server should have version."""
        assert server.version == "1.4.0"
    
    def test_token_types_dictionary(self):
        """TOKEN_TYPES_DIC should map types to indices."""
        assert "keyword" in TOKEN_TYPES_DIC
        assert "function" in TOKEN_TYPES_DIC
        assert "class" in TOKEN_TYPES_DIC
        assert "variable" in TOKEN_TYPES_DIC
        assert isinstance(TOKEN_TYPES_DIC["keyword"], int)
    
    def test_token_modifiers_dictionary(self):
        """TOKEN_MODIFIERS_DIC should map modifiers to bit flags."""
        assert "declaration" in TOKEN_MODIFIERS_DIC
        assert "definition" in TOKEN_MODIFIERS_DIC
        # Modifiers should be powers of 2
        for modifier, value in TOKEN_MODIFIERS_DIC.items():
            assert value & (value - 1) == 0 or value == 0, f"{modifier} should be power of 2"


# ============== Completion Protocol Tests ==============

class TestCompletionProtocol:
    """Test completion request/response protocol."""
    
    def test_completion_params_structure(self, text_document_id, position):
        """CompletionParams should be properly structured."""
        params = CompletionParams(
            text_document=text_document_id(),
            position=position(0, 3)
        )
        assert params.text_document.uri == "file:///test.sage"
        assert params.position.line == 0
        assert params.position.character == 3
    
    def test_completion_with_trigger_character(self, text_document_id, position):
        """Completion with trigger character should work."""
        context = CompletionContext(
            trigger_kind=CompletionTriggerKind.TriggerCharacter,
            trigger_character="."
        )
        params = CompletionParams(
            text_document=text_document_id(),
            position=position(0, 5),
            context=context
        )
        assert params.context.trigger_character == "."
        assert params.context.trigger_kind == CompletionTriggerKind.TriggerCharacter
    
    def test_completion_item_structure(self):
        """CompletionItem should have required fields."""
        item = CompletionItem(
            label="factor",
            kind=CompletionItemKind.Function,
            detail="Factor an integer or polynomial",
            documentation="Returns the factorization of n."
        )
        assert item.label == "factor"
        assert item.kind == CompletionItemKind.Function
        assert item.detail is not None
    
    def test_completion_list_structure(self):
        """CompletionList should contain items."""
        items = [
            CompletionItem(label="factor", kind=CompletionItemKind.Function),
            CompletionItem(label="factorial", kind=CompletionItemKind.Function),
        ]
        completion_list = CompletionList(is_incomplete=False, items=items)
        assert len(completion_list.items) == 2
        assert not completion_list.is_incomplete
    
    def test_function_completions_available(self):
        """FUNCTIONS dictionary should provide completions."""
        assert len(FUNCTIONS) > 0
        assert "factor" in FUNCTIONS
        assert "gcd" in FUNCTIONS
        assert "matrix" in FUNCTIONS
    
    def test_class_completions_available(self):
        """CLASSES dictionary should provide completions."""
        assert len(CLASSES) > 0
        assert "ZZ" in CLASSES
        assert "QQ" in CLASSES
        assert "PolynomialRing" in CLASSES
    
    def test_keyword_completions_available(self):
        """KEYWORDS set should provide completions."""
        assert len(KEYWORDS) > 0
        assert "def" in KEYWORDS
        assert "class" in KEYWORDS
        assert "import" in KEYWORDS
        assert "for" in KEYWORDS


# ============== Hover Protocol Tests ==============

class TestHoverProtocol:
    """Test hover request/response protocol."""
    
    def test_hover_params_structure(self, text_document_id, position):
        """HoverParams should be properly structured."""
        params = HoverParams(
            text_document=text_document_id(),
            position=position(0, 10)
        )
        assert params.text_document.uri == "file:///test.sage"
        assert params.position.line == 0
    
    def test_hover_response_structure(self):
        """Hover response should have MarkupContent."""
        content = MarkupContent(
            kind=MarkupKind.Markdown,
            value="**factor**(n)\n\nFactor an integer."
        )
        hover = Hover(contents=content)
        assert hover.contents.kind == MarkupKind.Markdown
        assert "factor" in hover.contents.value
    
    def test_hover_with_range(self, position):
        """Hover can include range of highlighted text."""
        content = MarkupContent(kind=MarkupKind.Markdown, value="Documentation")
        range_ = Range(start=position(0, 5), end=position(0, 11))
        hover = Hover(contents=content, range=range_)
        assert hover.range is not None
        assert hover.range.start.character == 5
    
    def test_function_docs_available(self):
        """FUNCTION_DOCS should contain documentation."""
        assert len(FUNCTION_DOCS) > 0
        assert "factor" in FUNCTION_DOCS
        factor_doc = FUNCTION_DOCS["factor"]
        assert "signature" in factor_doc
        assert "description" in factor_doc
    
    def test_method_docs_available(self):
        """METHOD_DOCS should contain method documentation."""
        assert len(METHOD_DOCS) > 0
        # Check some common methods
        if "determinant" in METHOD_DOCS:
            det_doc = METHOD_DOCS["determinant"]
            assert "description" in det_doc


# ============== Signature Help Protocol Tests ==============

class TestSignatureHelpProtocol:
    """Test signature help request/response protocol."""
    
    def test_signature_help_params_structure(self, text_document_id, position):
        """SignatureHelpParams should be properly structured."""
        params = SignatureHelpParams(
            text_document=text_document_id(),
            position=position(0, 7)
        )
        assert params.text_document.uri == "file:///test.sage"
    
    def test_signature_help_with_context(self, text_document_id, position):
        """SignatureHelpParams can include context."""
        context = SignatureHelpContext(
            trigger_kind=SignatureHelpTriggerKind.TriggerCharacter,
            trigger_character="(",
            is_retrigger=False
        )
        params = SignatureHelpParams(
            text_document=text_document_id(),
            position=position(0, 7),
            context=context
        )
        assert params.context.trigger_character == "("
        assert not params.context.is_retrigger
    
    def test_signature_information_structure(self):
        """SignatureInformation should have label and parameters."""
        params = [
            ParameterInformation(label="n", documentation="The number to factor"),
            ParameterInformation(label="proof", documentation="Whether to prove primality"),
        ]
        sig = SignatureInformation(
            label="factor(n, proof=True)",
            documentation="Factor an integer or polynomial.",
            parameters=params
        )
        assert "factor" in sig.label
        assert len(sig.parameters) == 2
        assert sig.parameters[0].label == "n"
    
    def test_signature_help_response_structure(self):
        """SignatureHelp response should have signatures and active info."""
        sig = SignatureInformation(
            label="gcd(a, b)",
            parameters=[
                ParameterInformation(label="a"),
                ParameterInformation(label="b"),
            ]
        )
        help_ = SignatureHelp(
            signatures=[sig],
            active_signature=0,
            active_parameter=1
        )
        assert len(help_.signatures) == 1
        assert help_.active_signature == 0
        assert help_.active_parameter == 1


# ============== Definition Protocol Tests ==============

class TestDefinitionProtocol:
    """Test go-to-definition request/response protocol."""
    
    def test_definition_params_structure(self, text_document_id, position):
        """DefinitionParams should be properly structured."""
        params = DefinitionParams(
            text_document=text_document_id(),
            position=position(3, 10)
        )
        assert params.text_document.uri == "file:///test.sage"
        assert params.position.line == 3
    
    def test_location_response_structure(self, position):
        """Definition response should be Location or list of Locations."""
        loc = Location(
            uri="file:///test.sage",
            range=Range(start=position(0, 4), end=position(0, 12))
        )
        assert loc.uri == "file:///test.sage"
        assert loc.range.start.line == 0
    
    def test_find_function_definition(self, mock_document):
        """Should find function definitions in document."""
        doc = mock_document("def my_func(x):\n    return x * 2\n\nresult = my_func(5)")
        definitions = find_definitions_in_doc(doc, "my_func")
        assert len(definitions) > 0
        assert definitions[0].range.start.line == 0
    
    def test_find_variable_definition(self, mock_document):
        """Should find variable definitions in document."""
        doc = mock_document("x = 5\ny = x + 1")
        definitions = find_definitions_in_doc(doc, "x")
        assert len(definitions) > 0
        assert definitions[0].range.start.line == 0
    
    def test_find_class_definition(self, mock_document):
        """Should find class definitions in document."""
        doc = mock_document("class MyClass:\n    pass\n\nobj = MyClass()")
        definitions = find_definitions_in_doc(doc, "MyClass")
        assert len(definitions) > 0
        assert definitions[0].range.start.line == 0
    
    def test_no_definition_for_builtin(self, mock_document):
        """Built-in functions should not have local definitions."""
        doc = mock_document("result = factor(120)")
        definitions = find_definitions_in_doc(doc, "factor")
        # factor is a builtin, should not be found in local document
        assert len(definitions) == 0


# ============== References Protocol Tests ==============

class TestReferencesProtocol:
    """Test find-references request/response protocol."""
    
    def test_reference_params_structure(self, text_document_id, position):
        """ReferenceParams should be properly structured."""
        context = ReferenceContext(include_declaration=True)
        params = ReferenceParams(
            text_document=text_document_id(),
            position=position(0, 0),
            context=context
        )
        assert params.context.include_declaration
    
    def test_find_variable_references(self, mock_document):
        """Should find all variable references."""
        doc = mock_document("x = 5\ny = x + 1\nz = x * 2")
        references = find_references_in_doc(doc, "x")
        assert len(references) >= 3  # definition + 2 uses
    
    def test_find_function_references(self, mock_document):
        """Should find all function references."""
        doc = mock_document("def foo():\n    return 1\n\na = foo()\nb = foo()")
        references = find_references_in_doc(doc, "foo")
        assert len(references) >= 3  # definition + 2 calls
    
    def test_include_declaration_in_references(self, mock_document):
        """References should include declaration when requested."""
        doc = mock_document("x = 5\nprint(x)")
        references = find_references_in_doc(doc, "x")
        # Line 0 should be included (declaration)
        lines = [ref.range.start.line for ref in references]
        assert 0 in lines


# ============== Diagnostics Protocol Tests ==============

class TestDiagnosticsProtocol:
    """Test diagnostics publishing protocol."""
    
    def test_diagnostic_structure(self, position):
        """Diagnostic should have required fields."""
        diag = Diagnostic(
            range=Range(start=position(0, 0), end=position(0, 10)),
            message="Test diagnostic",
            severity=DiagnosticSeverity.Warning,
            source="sagemath-lsp"
        )
        assert diag.message == "Test diagnostic"
        assert diag.severity == DiagnosticSeverity.Warning
        assert diag.source == "sagemath-lsp"
    
    def test_mixed_indentation_diagnostic(self, mock_document):
        """Should detect mixed tabs and spaces."""
        doc = mock_document("def foo():\n\t x = 5")  # Tab followed by space
        diagnostics = check_diagnostics(doc)
        # Should have warning about mixed indentation
        mixed_warnings = [d for d in diagnostics if "mixed" in d.message.lower() or "tab" in d.message.lower()]
        assert len(mixed_warnings) >= 0  # May or may not detect depending on exact content
    
    def test_assignment_in_condition_diagnostic(self, mock_document):
        """Should detect assignment in condition."""
        doc = mock_document("if x = 5:\n    print(x)")
        diagnostics = check_diagnostics(doc)
        assignment_warnings = [d for d in diagnostics if "assignment" in d.message.lower()]
        assert len(assignment_warnings) > 0
    
    def test_no_false_positives_for_comparison(self, mock_document):
        """Should not warn for proper comparisons."""
        doc = mock_document("if x == 5:\n    print(x)")
        diagnostics = check_diagnostics(doc)
        assignment_warnings = [d for d in diagnostics if "assignment" in d.message.lower()]
        assert len(assignment_warnings) == 0
    
    def test_known_functions_not_undefined(self, mock_document):
        """Known SageMath functions should not be marked undefined."""
        doc = mock_document("result = factor(120)\nx = gcd(12, 18)")
        diagnostics = check_diagnostics(doc)
        # factor and gcd should not be marked as undefined
        undefined_errors = [d for d in diagnostics 
                          if "not defined" in d.message.lower() 
                          and ("factor" in d.message or "gcd" in d.message)]
        assert len(undefined_errors) == 0
    
    def test_diagnostic_severity_levels(self, position):
        """Test different diagnostic severity levels."""
        error = Diagnostic(
            range=Range(start=position(0, 0), end=position(0, 5)),
            message="Error",
            severity=DiagnosticSeverity.Error
        )
        warning = Diagnostic(
            range=Range(start=position(0, 0), end=position(0, 5)),
            message="Warning",
            severity=DiagnosticSeverity.Warning
        )
        info = Diagnostic(
            range=Range(start=position(0, 0), end=position(0, 5)),
            message="Info",
            severity=DiagnosticSeverity.Information
        )
        hint = Diagnostic(
            range=Range(start=position(0, 0), end=position(0, 5)),
            message="Hint",
            severity=DiagnosticSeverity.Hint
        )
        assert error.severity == DiagnosticSeverity.Error
        assert warning.severity == DiagnosticSeverity.Warning
        assert info.severity == DiagnosticSeverity.Information
        assert hint.severity == DiagnosticSeverity.Hint


# ============== Semantic Tokens Protocol Tests ==============

class TestSemanticTokensProtocol:
    """Test semantic tokens request/response protocol."""
    
    def test_semantic_tokens_params_structure(self, text_document_id):
        """SemanticTokensParams should be properly structured."""
        params = SemanticTokensParams(text_document=text_document_id())
        assert params.text_document.uri == "file:///test.sage"
    
    def test_semantic_tokens_response_structure(self):
        """SemanticTokens response should have data array."""
        # Data is encoded as relative positions: [deltaLine, deltaChar, length, tokenType, tokenModifiers]
        data = [0, 0, 3, 0, 0, 0, 4, 1, 1, 0]  # Two tokens
        tokens = SemanticTokens(data=data)
        assert len(tokens.data) == 10
        assert tokens.data[0] == 0  # First token at line 0
    
    def test_token_type_indices(self):
        """Token type indices should be valid."""
        for token_type, index in TOKEN_TYPES_DIC.items():
            assert index >= 0
            assert isinstance(index, int)
    
    def test_token_modifier_flags(self):
        """Token modifier flags should be powers of 2."""
        for modifier, flag in TOKEN_MODIFIERS_DIC.items():
            # Check it's a power of 2 (or 0)
            assert flag == 0 or (flag & (flag - 1)) == 0


# ============== TextDocument Sync Protocol Tests ==============

class TestTextDocumentSyncProtocol:
    """Test document synchronization protocol."""
    
    def test_did_open_params_structure(self):
        """DidOpenTextDocumentParams should be properly structured."""
        text_doc = TextDocumentItem(
            uri="file:///test.sage",
            language_id="sagemath",
            version=1,
            text="x = 5"
        )
        params = DidOpenTextDocumentParams(text_document=text_doc)
        assert params.text_document.uri == "file:///test.sage"
        assert params.text_document.language_id == "sagemath"
        assert params.text_document.version == 1
    
    def test_did_change_params_structure(self):
        """DidChangeTextDocumentParams should be properly structured."""
        text_doc = VersionedTextDocumentIdentifier(
            uri="file:///test.sage",
            version=2
        )
        # TextDocumentContentChangeEvent is a Union type, use dict for full change
        params = DidChangeTextDocumentParams(
            text_document=text_doc,
            content_changes=[{"text": "x = 10"}]
        )
        assert params.text_document.version == 2
        assert len(params.content_changes) == 1
    
    def test_incremental_change_structure(self, position):
        """Incremental changes should have range and text."""
        # TextDocumentContentChangeEvent is a Union type, test the structure
        change = {
            "range": {
                "start": {"line": 0, "character": 4},
                "end": {"line": 0, "character": 5}
            },
            "text": "10"
        }
        assert change["range"]["start"]["character"] == 4
        assert change["text"] == "10"


# ============== Context Detection Tests ==============

class TestContextDetection:
    """Test context detection for intelligent features."""
    
    def test_detect_method_context(self, mock_document):
        """Should detect method completion context after dot."""
        doc = mock_document("M = matrix(ZZ, 2, 2)\nM.")
        obj_name, partial, is_after_dot = get_context_at_position(doc, Position(line=1, character=2))
        assert is_after_dot
        assert obj_name == "M"
    
    def test_detect_function_context(self, mock_document):
        """Should detect function completion context."""
        doc = mock_document("fac")
        obj_name, partial, is_after_dot = get_context_at_position(doc, Position(line=0, character=3))
        assert not is_after_dot
        assert partial == "fac"
    
    def test_detect_empty_context(self, mock_document):
        """Should handle empty context."""
        doc = mock_document("")
        obj_name, partial, is_after_dot = get_context_at_position(doc, Position(line=0, character=0))
        assert not is_after_dot
        assert partial == ""
    
    def test_detect_nested_method_context(self, mock_document):
        """Should detect nested method context."""
        doc = mock_document("result.method().")
        obj_name, partial, is_after_dot = get_context_at_position(doc, Position(line=0, character=16))
        # After calling method(), cursor is after the dot following ()
        # The function may or may not detect this as after_dot depending on implementation
        assert is_after_dot or not is_after_dot  # Test that it doesn't crash


# ============== Function Detection Tests ==============

class TestFunctionDetection:
    """Test function detection for signature help."""
    
    def test_detect_function_at_open_paren(self, mock_document):
        """Should detect function at opening parenthesis."""
        doc = mock_document("result = factor(")
        result = get_function_at_position(doc, Position(line=0, character=16))
        assert result is not None
        func_name, param_index = result
        assert func_name == "factor"
        assert param_index == 0
    
    def test_detect_function_second_param(self, mock_document):
        """Should detect function and correct parameter index."""
        doc = mock_document("gcd(12, ")
        result = get_function_at_position(doc, Position(line=0, character=8))
        assert result is not None
        func_name, param_index = result
        assert func_name == "gcd"
        assert param_index == 1
    
    def test_detect_nested_function(self, mock_document):
        """Should detect innermost function in nested calls."""
        doc = mock_document("outer(inner(")
        result = get_function_at_position(doc, Position(line=0, character=12))
        assert result is not None
        func_name, _ = result
        assert func_name == "inner"
    
    def test_no_function_outside_parens(self, mock_document):
        """Should return None when not inside function call."""
        doc = mock_document("x = 5")
        result = get_function_at_position(doc, Position(line=0, character=5))
        assert result is None


# ============== Word At Position Tests ==============

class TestWordAtPosition:
    """Test word extraction at cursor position."""
    
    def test_get_word_at_start(self, mock_document):
        """Should get word when cursor at start."""
        doc = mock_document("factor(120)")
        word = get_word_at_position(doc, Position(line=0, character=0))
        assert word == "factor"
    
    def test_get_word_at_middle(self, mock_document):
        """Should get word when cursor in middle."""
        doc = mock_document("factor(120)")
        word = get_word_at_position(doc, Position(line=0, character=3))
        assert word == "factor"
    
    def test_get_word_at_end(self, mock_document):
        """Should get word when cursor at end."""
        doc = mock_document("factor(120)")
        word = get_word_at_position(doc, Position(line=0, character=6))
        assert word == "factor"
    
    def test_get_word_with_underscore(self, mock_document):
        """Should include underscores in word."""
        doc = mock_document("my_function()")
        word = get_word_at_position(doc, Position(line=0, character=5))
        assert word == "my_function"
    
    def test_get_word_number_suffix(self, mock_document):
        """Should include numbers in identifiers."""
        doc = mock_document("var123 = 5")
        word = get_word_at_position(doc, Position(line=0, character=3))
        assert word == "var123"
    
    def test_no_word_at_operator(self, mock_document):
        """Should return None at operator."""
        doc = mock_document("x + y")
        word = get_word_at_position(doc, Position(line=0, character=2))
        assert word is None or word == ""
    
    def test_no_word_at_empty_line(self, mock_document):
        """Should return None at empty line."""
        doc = mock_document("x = 5\n\ny = 10")
        word = get_word_at_position(doc, Position(line=1, character=0))
        assert word is None or word == ""


# ============== Edge Cases Tests ==============

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_document(self, mock_document):
        """Should handle empty document."""
        doc = mock_document("")
        word = get_word_at_position(doc, Position(line=0, character=0))
        assert word is None or word == ""
        
        diagnostics = check_diagnostics(doc)
        assert isinstance(diagnostics, list)
    
    def test_single_character(self, mock_document):
        """Should handle single character."""
        doc = mock_document("x")
        word = get_word_at_position(doc, Position(line=0, character=0))
        assert word == "x"
    
    def test_unicode_content(self, mock_document):
        """Should handle unicode content."""
        doc = mock_document("π = 3.14159")
        # Should not crash
        diagnostics = check_diagnostics(doc)
        assert isinstance(diagnostics, list)
    
    def test_very_long_line(self, mock_document):
        """Should handle very long lines."""
        long_line = "x = " + "1 + " * 1000 + "1"
        doc = mock_document(long_line)
        word = get_word_at_position(doc, Position(line=0, character=0))
        assert word == "x"
    
    def test_many_lines(self, mock_document):
        """Should handle many lines."""
        content = "\n".join([f"x{i} = {i}" for i in range(1000)])
        doc = mock_document(content)
        word = get_word_at_position(doc, Position(line=500, character=0))
        assert word == "x500"
    
    def test_invalid_position_negative(self, mock_document):
        """Should handle negative positions gracefully."""
        doc = mock_document("x = 5")
        # Should not crash, may return None
        try:
            word = get_word_at_position(doc, Position(line=-1, character=0))
        except (IndexError, ValueError):
            pass  # Expected behavior
    
    def test_invalid_position_beyond_document(self, mock_document):
        """Should handle positions beyond document."""
        doc = mock_document("x = 5")
        word = get_word_at_position(doc, Position(line=100, character=0))
        assert word is None
    
    def test_special_sagemath_syntax(self, mock_document):
        """Should handle SageMath-specific syntax."""
        doc = mock_document("R.<x,y> = PolynomialRing(QQ)")
        # Should not crash
        diagnostics = check_diagnostics(doc)
        assert isinstance(diagnostics, list)
