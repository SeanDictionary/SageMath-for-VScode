"""
Pytest configuration and shared fixtures for SageMath LSP tests.
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lsprotocol.types import Position, Range
from utils import Token, Logging


class MockTextDocument:
    """Mock TextDocument for testing LSP functions."""
    
    def __init__(self, content: str, uri: str = "file:///test.sage"):
        self.uri = uri
        self._content = content
        self._lines: Optional[list[str]] = None
    
    @property
    def lines(self) -> list[str]:
        if self._lines is None:
            self._lines = self._content.split('\n')
        return self._lines
    
    @property
    def source(self) -> str:
        return self._content


class MockLanguageServer:
    """Mock Language Server for testing."""
    
    def __init__(self):
        self.log_level = "info"
        self.log = Logging(self._mock_log, self.log_level)
        self._log_messages: list[str] = []
        self._published_diagnostics: list[tuple] = []
    
    def _mock_log(self, message: str):
        self._log_messages.append(message)
    
    def show_message_log(self, message: str):
        self._log_messages.append(message)
    
    def publish_diagnostics(self, uri: str, diagnostics: list):
        self._published_diagnostics.append((uri, diagnostics))


@pytest.fixture
def mock_document():
    """Factory fixture to create mock documents."""
    def _create_document(content: str, uri: str = "file:///test.sage") -> MockTextDocument:
        return MockTextDocument(content, uri)
    return _create_document


@pytest.fixture
def mock_ls():
    """Create a mock language server."""
    return MockLanguageServer()


@pytest.fixture
def simple_document(mock_document):
    """A simple test document with basic SageMath code."""
    content = """# Test file
x = 5
y = 10
def foo(a, b):
    return a + b

result = foo(x, y)
"""
    return mock_document(content)


@pytest.fixture
def class_document(mock_document):
    """A test document with class definition."""
    content = """class MyClass:
    def __init__(self, value):
        self.value = value
    
    def get_value(self):
        return self.value

obj = MyClass(42)
result = obj.get_value()
"""
    return mock_document(content)


@pytest.fixture
def sagemath_document(mock_document):
    """A test document with SageMath-specific code."""
    content = """from sage.all import *

R.<x> = PolynomialRing(QQ)
p = x^2 + 2*x + 1
roots = p.roots()

M = matrix(ZZ, [[1, 2], [3, 4]])
det_M = M.det()

E = EllipticCurve(GF(101), [0, 7])
order = E.order()
"""
    return mock_document(content)


@pytest.fixture
def diagnostic_document(mock_document):
    """A document with various diagnostic issues."""
    content = """\t x = 5
if x = 5:
    print("hello")
undefined_func()
"""
    return mock_document(content)


@pytest.fixture
def empty_document(mock_document):
    """An empty document."""
    return mock_document("")


@pytest.fixture
def position():
    """Factory fixture to create Position objects."""
    def _create_position(line: int, character: int) -> Position:
        return Position(line=line, character=character)
    return _create_position


@pytest.fixture
def sample_tokens():
    """Sample tokens for testing classification."""
    return [
        Token(line=0, offset=0, text="def"),
        Token(line=0, offset=4, text="foo"),
        Token(line=0, offset=7, text="(", tok_type="operator"),
        Token(line=0, offset=8, text="x"),
        Token(line=0, offset=9, text=")", tok_type="operator"),
        Token(line=0, offset=10, text=":", tok_type="operator"),
    ]
