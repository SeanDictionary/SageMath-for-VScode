"""
Symbol extraction and analysis module for SageMath LSP
Provides: Document symbols, user-defined symbol extraction, workspace symbols
"""

from __future__ import annotations
import re
from typing import Optional
from dataclasses import dataclass, field

from lsprotocol.types import (
    DocumentSymbol, SymbolKind, Range, Position,
    CompletionItem, CompletionItemKind, MarkupContent, MarkupKind
)


@dataclass
class UserSymbol:
    """Represents a user-defined symbol in the document"""
    name: str
    kind: SymbolKind
    line: int
    character: int
    end_line: int
    end_character: int
    detail: str = ""
    children: list["UserSymbol"] = field(default_factory=list)
    docstring: Optional[str] = None
    signature: Optional[str] = None
    inferred_type: Optional[str] = None


class SymbolExtractor:
    """Extract symbols from SageMath/Python documents"""
    
    # Patterns for symbol detection
    FUNCTION_PATTERN = re.compile(r'^(\s*)def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*(?:->([^:]+))?:')
    CLASS_PATTERN = re.compile(r'^(\s*)class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(([^)]*)\))?:')
    VARIABLE_PATTERN = re.compile(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)')
    MULTI_ASSIGN_PATTERN = re.compile(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)+)\s*=\s*(.+)')
    FOR_PATTERN = re.compile(r'^(\s*)for\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+in\s+')
    WITH_PATTERN = re.compile(r'^(\s*)with\s+.+\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:')
    IMPORT_PATTERN = re.compile(r'^(?:from\s+[\w.]+\s+)?import\s+(.+)')
    SAGE_VAR_PATTERN = re.compile(r"var\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
    SAGE_RING_PATTERN = re.compile(r'^(\s*)([A-Za-z_][A-Za-z0-9_]*)(?:\.<([^>]+)>)?\s*=\s*(PolynomialRing|GF|Zmod|NumberField|QuadraticField|FunctionField|PowerSeriesRing)')
    DOCSTRING_PATTERN = re.compile(r'^\s*"""(.+?)"""', re.DOTALL)
    DOCSTRING_START = re.compile(r'^\s*"""')
    
    # Type inference patterns
    TYPE_PATTERNS = {
        r'matrix\s*\(': 'Matrix',
        r'Matrix\s*\(': 'Matrix',
        r'vector\s*\(': 'Vector',
        r'EllipticCurve\s*\(': 'EllipticCurve',
        r'GF\s*\(': 'FiniteField',
        r'Zmod\s*\(': 'IntegerModRing',
        r'PolynomialRing\s*\(': 'PolynomialRing',
        r'NumberField\s*\(': 'NumberField',
        r'QuadraticField\s*\(': 'QuadraticField',
        r'Graph\s*\(': 'Graph',
        r'DiGraph\s*\(': 'DiGraph',
        r'Ideal\s*\(': 'Ideal',
        r'\.ideal\s*\(': 'Ideal',
        r'Integer\s*\(': 'Integer',
        r'Rational\s*\(': 'Rational',
        r'RealNumber\s*\(': 'RealNumber',
        r'\[\s*\[': 'Matrix',  # [[...]] likely a matrix
        r'\[.*\]': 'list',
        r'\{.*\}': 'dict',
        r'\(.*,.*\)': 'tuple',
        r'range\s*\(': 'range',
        r'set\s*\(': 'set',
        r'frozenset\s*\(': 'frozenset',
        r'"\s*"': 'str',
        r"'\s*'": 'str',
        r'\d+\.\d+': 'float',
        r'\d+': 'int',
        r'True|False': 'bool',
        r'None': 'NoneType',
    }
    
    def __init__(self):
        self.symbols: list[UserSymbol] = []
        self.flat_symbols: dict[str, UserSymbol] = {}
    
    def extract_symbols(self, lines: list[str]) -> list[UserSymbol]:
        """Extract all symbols from document lines"""
        self.symbols = []
        self.flat_symbols = {}
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                i += 1
                continue
            
            # Check for class definition
            class_match = self.CLASS_PATTERN.match(line)
            if class_match:
                symbol = self._extract_class(lines, i, class_match)
                if symbol:
                    self.symbols.append(symbol)
                    self.flat_symbols[symbol.name] = symbol
                i += 1
                continue
            
            # Check for function definition
            func_match = self.FUNCTION_PATTERN.match(line)
            if func_match:
                symbol = self._extract_function(lines, i, func_match)
                if symbol:
                    self.symbols.append(symbol)
                    self.flat_symbols[symbol.name] = symbol
                i += 1
                continue
            
            # Check for SageMath ring definition (R.<x> = PolynomialRing(...))
            ring_match = self.SAGE_RING_PATTERN.match(line)
            if ring_match:
                symbols = self._extract_ring_definition(lines, i, ring_match)
                for sym in symbols:
                    self.symbols.append(sym)
                    self.flat_symbols[sym.name] = sym
                i += 1
                continue
            
            # Check for multi-assignment (a, b, c = ...)
            multi_match = self.MULTI_ASSIGN_PATTERN.match(line)
            if multi_match:
                symbols = self._extract_multi_assignment(lines, i, multi_match)
                for sym in symbols:
                    self.symbols.append(sym)
                    self.flat_symbols[sym.name] = sym
                i += 1
                continue
            
            # Check for variable assignment
            var_match = self.VARIABLE_PATTERN.match(line)
            if var_match:
                symbol = self._extract_variable(lines, i, var_match)
                if symbol:
                    self.symbols.append(symbol)
                    self.flat_symbols[symbol.name] = symbol
                i += 1
                continue
            
            # Check for var('x y z') symbolic variables
            var_decl = self.SAGE_VAR_PATTERN.search(line)
            if var_decl:
                symbols = self._extract_sage_vars(lines, i, var_decl)
                for sym in symbols:
                    self.symbols.append(sym)
                    self.flat_symbols[sym.name] = sym
                i += 1
                continue
            
            # Check for for-loop variable
            for_match = self.FOR_PATTERN.match(line)
            if for_match:
                symbol = self._extract_for_variable(lines, i, for_match)
                if symbol:
                    self.symbols.append(symbol)
                    self.flat_symbols[symbol.name] = symbol
                i += 1
                continue
            
            # Check for with-as variable
            with_match = self.WITH_PATTERN.match(line)
            if with_match:
                symbol = self._extract_with_variable(lines, i, with_match)
                if symbol:
                    self.symbols.append(symbol)
                    self.flat_symbols[symbol.name] = symbol
                i += 1
                continue
            
            i += 1
        
        return self.symbols
    
    def _extract_function(self, lines: list[str], line_num: int, match: re.Match) -> Optional[UserSymbol]:
        """Extract function definition"""
        indent, name, params, return_type = match.groups()
        indent_level = len(indent) if indent else 0
        
        # Get docstring if present
        docstring = self._get_docstring(lines, line_num + 1)
        
        # Build signature
        signature = f"def {name}({params})"
        if return_type:
            signature += f" -> {return_type.strip()}"
        
        # Find function end
        end_line = self._find_block_end(lines, line_num, indent_level)
        
        return UserSymbol(
            name=name,
            kind=SymbolKind.Function,
            line=line_num,
            character=indent_level,
            end_line=end_line,
            end_character=0,
            detail=f"({params})" if params else "()",
            docstring=docstring,
            signature=signature
        )
    
    def _extract_class(self, lines: list[str], line_num: int, match: re.Match) -> Optional[UserSymbol]:
        """Extract class definition"""
        indent, name, bases = match.groups()
        indent_level = len(indent) if indent else 0
        
        # Get docstring if present
        docstring = self._get_docstring(lines, line_num + 1)
        
        # Find class end
        end_line = self._find_block_end(lines, line_num, indent_level)
        
        detail = f"({bases})" if bases else ""
        
        return UserSymbol(
            name=name,
            kind=SymbolKind.Class,
            line=line_num,
            character=indent_level,
            end_line=end_line,
            end_character=0,
            detail=detail,
            docstring=docstring,
            signature=f"class {name}{detail}"
        )
    
    def _extract_variable(self, lines: list[str], line_num: int, match: re.Match) -> Optional[UserSymbol]:
        """Extract variable assignment"""
        indent, name, value = match.groups()
        indent_level = len(indent) if indent else 0
        
        # Skip private/dunder variables at module level for outline
        if name.startswith('_') and indent_level == 0:
            pass  # Still include but mark differently
        
        # Infer type from value
        inferred_type = self._infer_type(value.strip())
        
        detail = f": {inferred_type}" if inferred_type else ""
        
        return UserSymbol(
            name=name,
            kind=SymbolKind.Variable,
            line=line_num,
            character=indent_level,
            end_line=line_num,
            end_character=len(lines[line_num]) if line_num < len(lines) else 0,
            detail=detail,
            inferred_type=inferred_type
        )
    
    def _extract_multi_assignment(self, lines: list[str], line_num: int, match: re.Match) -> list[UserSymbol]:
        """Extract multiple assignment (a, b = ...)"""
        indent, names_str, value = match.groups()
        indent_level = len(indent) if indent else 0
        
        names = [n.strip() for n in names_str.split(',')]
        symbols = []
        
        for i, name in enumerate(names):
            symbols.append(UserSymbol(
                name=name,
                kind=SymbolKind.Variable,
                line=line_num,
                character=indent_level,
                end_line=line_num,
                end_character=len(lines[line_num]) if line_num < len(lines) else 0,
                detail=""
            ))
        
        return symbols
    
    def _extract_ring_definition(self, lines: list[str], line_num: int, match: re.Match) -> list[UserSymbol]:
        """Extract SageMath ring definition like R.<x> = PolynomialRing(...)"""
        indent, ring_name, generators, ring_type = match.groups()
        indent_level = len(indent) if indent else 0
        
        symbols = []
        
        # Add the ring itself
        symbols.append(UserSymbol(
            name=ring_name,
            kind=SymbolKind.Variable,
            line=line_num,
            character=indent_level,
            end_line=line_num,
            end_character=len(lines[line_num]) if line_num < len(lines) else 0,
            detail=f": {ring_type}",
            inferred_type=ring_type
        ))
        
        # Add generators if present
        if generators:
            for gen in generators.split(','):
                gen = gen.strip()
                if gen:
                    symbols.append(UserSymbol(
                        name=gen,
                        kind=SymbolKind.Variable,
                        line=line_num,
                        character=indent_level,
                        end_line=line_num,
                        end_character=len(lines[line_num]) if line_num < len(lines) else 0,
                        detail=": generator",
                        inferred_type="generator"
                    ))
        
        return symbols
    
    def _extract_sage_vars(self, lines: list[str], line_num: int, match: re.Match) -> list[UserSymbol]:
        """Extract var('x y z') declarations"""
        var_names = match.group(1).split()
        symbols = []
        
        for name in var_names:
            name = name.strip().strip(',')
            if name:
                symbols.append(UserSymbol(
                    name=name,
                    kind=SymbolKind.Variable,
                    line=line_num,
                    character=0,
                    end_line=line_num,
                    end_character=len(lines[line_num]) if line_num < len(lines) else 0,
                    detail=": symbolic",
                    inferred_type="SR"
                ))
        
        return symbols
    
    def _extract_for_variable(self, lines: list[str], line_num: int, match: re.Match) -> Optional[UserSymbol]:
        """Extract for-loop variable"""
        indent, name = match.groups()
        indent_level = len(indent) if indent else 0
        
        return UserSymbol(
            name=name,
            kind=SymbolKind.Variable,
            line=line_num,
            character=indent_level,
            end_line=line_num,
            end_character=len(lines[line_num]) if line_num < len(lines) else 0,
            detail=": loop variable"
        )
    
    def _extract_with_variable(self, lines: list[str], line_num: int, match: re.Match) -> Optional[UserSymbol]:
        """Extract with-as variable"""
        indent, name = match.groups()
        indent_level = len(indent) if indent else 0
        
        return UserSymbol(
            name=name,
            kind=SymbolKind.Variable,
            line=line_num,
            character=indent_level,
            end_line=line_num,
            end_character=len(lines[line_num]) if line_num < len(lines) else 0,
            detail=": context manager"
        )
    
    def _infer_type(self, value: str) -> Optional[str]:
        """Infer type from assignment value"""
        for pattern, type_name in self.TYPE_PATTERNS.items():
            if re.search(pattern, value):
                return type_name
        return None
    
    def _get_docstring(self, lines: list[str], start_line: int) -> Optional[str]:
        """Extract docstring starting from given line"""
        if start_line >= len(lines):
            return None
        
        line = lines[start_line].strip()
        
        # Single line docstring
        single_match = re.match(r'^"""(.+)"""$', line)
        if single_match:
            return single_match.group(1).strip()
        
        single_match = re.match(r"^'''(.+)'''$", line)
        if single_match:
            return single_match.group(1).strip()
        
        # Multi-line docstring
        if line.startswith('"""') or line.startswith("'''"):
            quote = line[:3]
            docstring_lines = [line[3:]]
            for i in range(start_line + 1, min(start_line + 20, len(lines))):
                if quote in lines[i]:
                    docstring_lines.append(lines[i].split(quote)[0])
                    break
                docstring_lines.append(lines[i].strip())
            return '\n'.join(docstring_lines).strip()
        
        return None
    
    def _find_block_end(self, lines: list[str], start_line: int, base_indent: int) -> int:
        """Find the end of a code block (function/class)"""
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if not line.strip():
                continue
            if line.strip().startswith('#'):
                continue
            
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent and line.strip():
                return i - 1
        
        return len(lines) - 1
    
    def to_document_symbols(self) -> list[DocumentSymbol]:
        """Convert extracted symbols to LSP DocumentSymbol format"""
        return [self._user_symbol_to_doc_symbol(sym) for sym in self.symbols]
    
    def _user_symbol_to_doc_symbol(self, sym: UserSymbol) -> DocumentSymbol:
        """Convert UserSymbol to LSP DocumentSymbol"""
        return DocumentSymbol(
            name=sym.name,
            kind=sym.kind,
            range=Range(
                start=Position(line=sym.line, character=sym.character),
                end=Position(line=sym.end_line, character=sym.end_character)
            ),
            selection_range=Range(
                start=Position(line=sym.line, character=sym.character),
                end=Position(line=sym.line, character=sym.character + len(sym.name))
            ),
            detail=sym.detail,
            children=[self._user_symbol_to_doc_symbol(c) for c in sym.children]
        )
    
    def to_completion_items(self) -> list[CompletionItem]:
        """Convert extracted symbols to completion items"""
        items = []
        for sym in self.symbols:
            kind = CompletionItemKind.Variable
            if sym.kind == SymbolKind.Function:
                kind = CompletionItemKind.Function
            elif sym.kind == SymbolKind.Class:
                kind = CompletionItemKind.Class
            
            doc = ""
            if sym.docstring:
                doc = sym.docstring
            elif sym.inferred_type:
                doc = f"Type: {sym.inferred_type}"
            
            insert_text = sym.name
            if sym.kind == SymbolKind.Function:
                insert_text = f"{sym.name}("
            
            items.append(CompletionItem(
                label=sym.name,
                kind=kind,
                detail=sym.detail or sym.signature,
                documentation=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=doc
                ) if doc else None,
                insert_text=insert_text,
                sort_text=f"0_{sym.name}"  # User symbols sort first
            ))
        
        return items
    
    def get_symbol_at_position(self, line: int, character: int) -> Optional[UserSymbol]:
        """Get symbol at specific position"""
        for sym in self.symbols:
            if sym.line <= line <= sym.end_line:
                return sym
        return None
    
    def get_symbol_by_name(self, name: str) -> Optional[UserSymbol]:
        """Get symbol by name"""
        return self.flat_symbols.get(name)


def extract_document_symbols(lines: list[str]) -> list[DocumentSymbol]:
    """Convenience function to extract document symbols"""
    extractor = SymbolExtractor()
    extractor.extract_symbols(lines)
    return extractor.to_document_symbols()


def extract_completion_items(lines: list[str]) -> list[CompletionItem]:
    """Convenience function to extract completion items from user code"""
    extractor = SymbolExtractor()
    extractor.extract_symbols(lines)
    return extractor.to_completion_items()
