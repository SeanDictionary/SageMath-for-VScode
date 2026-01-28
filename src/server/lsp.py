"""
SageMath Language Server Protocol Implementation
Provides: Semantic Tokens, Code Completion, Hover, Signature Help, Diagnostics, Definition, References
"""

from __future__ import annotations
import re
from functools import reduce
from typing import Optional

from lsprotocol.types import (
    SemanticTokens, SemanticTokensParams, SemanticTokensLegend, InitializeParams,
    CompletionParams, CompletionList, CompletionItem, CompletionItemKind,
    CompletionOptions, HoverParams, Hover, MarkupContent, MarkupKind,
    SignatureHelpParams, SignatureHelp, SignatureInformation, ParameterInformation,
    SignatureHelpOptions, DefinitionParams, Location, ReferenceParams,
    DidOpenTextDocumentParams, DidChangeTextDocumentParams, DidSaveTextDocumentParams,
    Diagnostic, DiagnosticSeverity, PublishDiagnosticsParams, Position, Range,
    # New imports for enhanced features
    DocumentSymbol, DocumentSymbolParams, SymbolKind,
    FoldingRange, FoldingRangeParams, FoldingRangeKind,
    CodeAction, CodeActionParams, CodeActionKind, CodeActionOptions,
    TextEdit, WorkspaceEdit,
    RenameParams, PrepareRenameParams, RenameOptions,
    DocumentFormattingParams, FormattingOptions,
    InlayHint, InlayHintParams, InlayHintKind, InlayHintLabelPart,
    TextDocumentEdit, OptionalVersionedTextDocumentIdentifier,
)
from lsprotocol import types

from utils import Logging, SemanicSever
from predefinition import TOKEN_TYPES, TOKEN_MODIFIERS, FUNCTIONS, CLASSES, KEYWORDS
from documentation import (
    FUNCTION_DOCS, METHOD_DOCS, get_function_doc, get_method_doc,
    get_all_function_names, get_class_methods, format_hover_markdown, format_method_hover
)
from symbols import SymbolExtractor, extract_document_symbols, extract_completion_items
from code_actions import CodeActionProvider

TOKEN_TYPES_DIC = {s: i for i, s in enumerate(TOKEN_TYPES)}
TOKEN_MODIFIERS_DIC = {s: 2**i for i, s in enumerate(TOKEN_MODIFIERS)}

server = SemanicSever(name="sagemath-lsp", version="1.4.0")

# Code action provider instance
code_action_provider = CodeActionProvider()

# Document cache for symbols
document_symbols_cache: dict[str, list[DocumentSymbol]] = {}
symbol_extractor_cache: dict[str, SymbolExtractor] = {}

# Regex patterns for parsing
IDENTIFIER_PATTERN = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
FUNCTION_CALL_PATTERN = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')


# ============== Helper Functions ==============

def get_word_at_position(doc, position: Position) -> Optional[str]:
    """Get the word at the given position in the document."""
    try:
        line = doc.lines[position.line]
        # Find word boundaries
        start = position.character
        end = position.character
        
        while start > 0 and (line[start-1].isalnum() or line[start-1] == '_'):
            start -= 1
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        
        if start < end:
            return line[start:end]
    except (IndexError, AttributeError):
        pass
    return None


def get_context_at_position(doc, position: Position) -> tuple[Optional[str], Optional[str], bool]:
    """
    Get context at position for smart completion.
    Returns: (object_name, partial_text, is_after_dot)
    """
    try:
        line = doc.lines[position.line][:position.character]
        
        # Check if after a dot (method completion)
        if '.' in line:
            # Find the last dot and get object before it
            last_dot = line.rfind('.')
            before_dot = line[:last_dot].rstrip()
            after_dot = line[last_dot+1:]
            
            # Get object name
            match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*$', before_dot)
            if match:
                return match.group(1), after_dot, True
        
        # Regular identifier completion
        match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)$', line)
        if match:
            return None, match.group(1), False
        
        return None, "", False
    except (IndexError, AttributeError):
        return None, "", False


def get_function_at_position(doc, position: Position) -> Optional[tuple[str, int]]:
    """
    Get the function name and parameter index at cursor position.
    Returns: (function_name, param_index) or None
    """
    try:
        line = doc.lines[position.line][:position.character]
        
        # Count open/close parentheses to find the function
        paren_depth = 0
        func_start = -1
        param_index = 0
        
        for i in range(len(line) - 1, -1, -1):
            char = line[i]
            if char == ')':
                paren_depth += 1
            elif char == '(':
                if paren_depth == 0:
                    func_start = i
                    break
                paren_depth -= 1
            elif char == ',' and paren_depth == 0:
                param_index += 1
        
        if func_start > 0:
            # Find function name before the parenthesis
            before_paren = line[:func_start].rstrip()
            match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)$', before_paren)
            if match:
                return match.group(1), param_index
    except (IndexError, AttributeError):
        pass
    return None


def find_definitions_in_doc(doc, symbol: str) -> list[Location]:
    """Find where a symbol is defined in the document."""
    locations = []
    
    # Patterns for definitions
    patterns = [
        rf'\bdef\s+{re.escape(symbol)}\s*\(',  # function def
        rf'\bclass\s+{re.escape(symbol)}\s*[:\(]',  # class def
        rf'^{re.escape(symbol)}\s*=',  # variable assignment at line start
        rf'^\s+{re.escape(symbol)}\s*=',  # variable assignment with indent
        rf'\bfor\s+{re.escape(symbol)}\s+in\b',  # for loop variable
    ]
    
    for i, line in enumerate(doc.lines):
        for pattern in patterns:
            if re.search(pattern, line):
                col = line.find(symbol)
                if col >= 0:
                    locations.append(Location(
                        uri=doc.uri,
                        range=Range(
                            start=Position(line=i, character=col),
                            end=Position(line=i, character=col + len(symbol))
                        )
                    ))
                    break
    
    return locations


def find_references_in_doc(doc, symbol: str) -> list[Location]:
    """Find all references to a symbol in the document."""
    locations = []
    pattern = rf'\b{re.escape(symbol)}\b'
    
    for i, line in enumerate(doc.lines):
        for match in re.finditer(pattern, line):
            locations.append(Location(
                uri=doc.uri,
                range=Range(
                    start=Position(line=i, character=match.start()),
                    end=Position(line=i, character=match.end())
                )
            ))
    
    return locations


def check_diagnostics(doc) -> list[Diagnostic]:
    """Check document for potential issues."""
    diagnostics = []
    
    # Track defined names
    defined_vars = set()
    defined_funcs = set()
    defined_classes = set()
    
    # Add builtins and SageMath functions
    known_names = set(FUNCTIONS) | set(CLASSES.keys()) | set(KEYWORDS)
    known_names |= {'print', 'len', 'range', 'list', 'dict', 'set', 'tuple', 'str', 'int', 'float', 'bool', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr', 'open', 'input', 'map', 'filter', 'zip', 'enumerate', 'sorted', 'reversed', 'sum', 'min', 'max', 'any', 'all', 'True', 'False', 'None'}
    
    indent_stack = [0]
    
    for line_num, line in enumerate(doc.lines):
        stripped = line.rstrip()
        if not stripped or stripped.startswith('#'):
            continue
        
        # Check indentation consistency
        if stripped:
            indent = len(line) - len(line.lstrip())
            if line.lstrip() and not line.lstrip().startswith('#'):
                # Check for mixed tabs and spaces
                leading = line[:indent]
                if '\t' in leading and ' ' in leading:
                    diagnostics.append(Diagnostic(
                        range=Range(
                            start=Position(line=line_num, character=0),
                            end=Position(line=line_num, character=indent)
                        ),
                        message="Mixed tabs and spaces in indentation",
                        severity=DiagnosticSeverity.Warning,
                        source="sagemath-lsp"
                    ))
        
        # Track function definitions
        func_match = re.match(r'\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', stripped)
        if func_match:
            defined_funcs.add(func_match.group(1))
        
        # Track class definitions
        class_match = re.match(r'\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)', stripped)
        if class_match:
            defined_classes.add(class_match.group(1))
        
        # Track variable assignments
        assign_match = re.match(r'\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=(?!=)', stripped)
        if assign_match:
            defined_vars.add(assign_match.group(1))
        
        # Track for loop variables
        for_match = re.match(r'\s*for\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+in\b', stripped)
        if for_match:
            defined_vars.add(for_match.group(1))
        
        # Check for common syntax errors
        # Assignment in condition (if x = 5 instead of if x == 5)
        if_assign_match = re.search(r'\bif\s+[^:]*[^=!<>]=(?!=)[^=]', stripped)
        if if_assign_match and '==' not in stripped[if_assign_match.start():if_assign_match.end()+5]:
            diagnostics.append(Diagnostic(
                range=Range(
                    start=Position(line=line_num, character=if_assign_match.start()),
                    end=Position(line=line_num, character=if_assign_match.end())
                ),
                message="Possible assignment in condition. Did you mean '=='?",
                severity=DiagnosticSeverity.Warning,
                source="sagemath-lsp"
            ))
        
        # Check for undefined function calls (heuristic)
        for match in re.finditer(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', stripped):
            func_name = match.group(1)
            if func_name not in known_names and func_name not in defined_funcs and func_name not in defined_classes:
                # Skip if it looks like a method call
                pos = match.start()
                if pos > 0 and stripped[pos-1] == '.':
                    continue
                # This might be an undefined function - add as hint
                if not any(c.isupper() for c in func_name):  # Skip likely class names
                    diagnostics.append(Diagnostic(
                        range=Range(
                            start=Position(line=line_num, character=match.start()),
                            end=Position(line=line_num, character=match.start() + len(func_name))
                        ),
                        message=f"'{func_name}' may not be defined. Consider checking the spelling.",
                        severity=DiagnosticSeverity.Hint,
                        source="sagemath-lsp"
                    ))
    
    return diagnostics


# ============== Logging Configuration ==============
@server.feature('sagemath/loglevel')
def reload_config(ls: SemanicSever, params):
    ls.log_level = params.logLevel
    ls.log = Logging(ls.show_message_log, ls.log_level)


# ============== Initialize ==============
legend = SemanticTokensLegend(token_types=TOKEN_TYPES, token_modifiers=TOKEN_MODIFIERS)

@server.feature(types.INITIALIZE)
def initialize(ls: SemanicSever, params: InitializeParams):
    ls.log_level = "info"
    ls.log = Logging(ls.show_message_log, ls.log_level)
    ls.log.info("SageMath Language Server v1.3.0 initialized")
    ls.log.info("Features: Completion, Hover, SignatureHelp, Diagnostics, Definition, References")


# ============== Semantic Tokens ==============
@server.feature(types.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, legend)
def semantic_tokens(ls: SemanicSever, params: SemanticTokensParams) -> SemanticTokens:
    doc = ls.workspace.get_text_document(params.text_document.uri)
    tokens = ls.parse(doc)

    data = []
    for token in tokens:
        if not (token.tok_type in TOKEN_TYPES+[""] and all(mod in TOKEN_MODIFIERS for mod in token.tok_modifiers)):
            ls.log.warning(f"Invalid token type or modifiers: {token}")
            break
        data.extend([
            token.line,
            token.offset,
            len(token.text),
            TOKEN_TYPES_DIC[token.tok_type] if token.tok_type in TOKEN_TYPES else len(TOKEN_TYPES),
            reduce(lambda x, y: x | y, (TOKEN_MODIFIERS_DIC[mod] for mod in token.tok_modifiers), 0)
        ])

    return SemanticTokens(data=data)


# ============== Code Completion ==============
@server.feature(
    types.TEXT_DOCUMENT_COMPLETION,
    CompletionOptions(trigger_characters=['.', '('], resolve_provider=True)
)
def completions(ls: SemanicSever, params: CompletionParams) -> CompletionList:
    """Provide code completions."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    obj_name, partial, is_after_dot = get_context_at_position(doc, params.position)
    
    items = []
    partial_lower = partial.lower() if partial else ""
    
    # Add user-defined symbols first (they get priority in sorting)
    if not is_after_dot:
        user_items = get_user_completions(doc, partial)
        items.extend(user_items)
    
    if is_after_dot and obj_name:
        # Method completion for known classes
        ls.log.debug(f"Method completion for: {obj_name}")
        
        # Check if obj_name is a known class type
        for class_name, methods in METHOD_DOCS.items():
            if obj_name.lower() == class_name.lower() or obj_name in CLASSES:
                for method_name, method_doc in methods.items():
                    if not partial_lower or method_name.lower().startswith(partial_lower):
                        items.append(CompletionItem(
                            label=method_name,
                            kind=CompletionItemKind.Method,
                            detail=method_doc.get("signature", f"{method_name}()"),
                            documentation=MarkupContent(
                                kind=MarkupKind.Markdown,
                                value=method_doc.get("description", "")
                            ),
                            insert_text=f"{method_name}()"
                        ))
                break
        
        # Also add methods from CLASSES in predefinition
        if obj_name in CLASSES:
            class_info = CLASSES[obj_name]
            for method in class_info.get("methods", []):
                if not partial_lower or method.lower().startswith(partial_lower):
                    if not any(item.label == method for item in items):
                        items.append(CompletionItem(
                            label=method,
                            kind=CompletionItemKind.Method,
                            detail=f"{method}()",
                            insert_text=f"{method}()"
                        ))
    else:
        # Global completion
        ls.log.debug(f"Global completion, partial: {partial}")
        
        # Add functions
        for func_name in FUNCTIONS:
            if not partial_lower or func_name.lower().startswith(partial_lower):
                doc_info = get_function_doc(func_name)
                if doc_info:
                    items.append(CompletionItem(
                        label=func_name,
                        kind=CompletionItemKind.Function,
                        detail=doc_info["signature"],
                        documentation=MarkupContent(
                            kind=MarkupKind.Markdown,
                            value=doc_info["description"]
                        ),
                        insert_text=f"{func_name}("
                    ))
                else:
                    items.append(CompletionItem(
                        label=func_name,
                        kind=CompletionItemKind.Function,
                        insert_text=f"{func_name}("
                    ))
        
        # Add classes
        for class_name in CLASSES.keys():
            if not partial_lower or class_name.lower().startswith(partial_lower):
                doc_info = get_function_doc(class_name)
                if doc_info:
                    items.append(CompletionItem(
                        label=class_name,
                        kind=CompletionItemKind.Class,
                        detail=doc_info.get("signature", class_name),
                        documentation=MarkupContent(
                            kind=MarkupKind.Markdown,
                            value=doc_info.get("description", "")
                        )
                    ))
                else:
                    items.append(CompletionItem(
                        label=class_name,
                        kind=CompletionItemKind.Class
                    ))
        
        # Add keywords
        for keyword in KEYWORDS:
            if not partial_lower or keyword.lower().startswith(partial_lower):
                items.append(CompletionItem(
                    label=keyword,
                    kind=CompletionItemKind.Keyword
                ))
    
    ls.log.debug(f"Returning {len(items)} completion items")
    return CompletionList(is_incomplete=False, items=items)


# ============== Hover Documentation ==============
@server.feature(types.TEXT_DOCUMENT_HOVER)
def hover(ls: SemanicSever, params: HoverParams) -> Optional[Hover]:
    """Provide hover documentation."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    word = get_word_at_position(doc, params.position)
    
    if not word:
        return None
    
    ls.log.debug(f"Hover request for: {word}")
    
    # Check if it's a function
    func_doc = get_function_doc(word)
    if func_doc:
        markdown = format_hover_markdown(word, func_doc)
        return Hover(
            contents=MarkupContent(kind=MarkupKind.Markdown, value=markdown),
            range=Range(
                start=Position(line=params.position.line, character=params.position.character),
                end=Position(line=params.position.line, character=params.position.character + len(word))
            )
        )
    
    # Check if it's a class
    if word in CLASSES:
        class_info = CLASSES[word]
        methods = class_info.get("methods", [])
        method_list = ", ".join(methods[:10])
        if len(methods) > 10:
            method_list += f", ... ({len(methods)} methods)"
        
        markdown = f"### {word}\n\n**Class**\n\n**Methods:** {method_list}"
        return Hover(
            contents=MarkupContent(kind=MarkupKind.Markdown, value=markdown)
        )
    
    # Check if it's a method (look for dot before)
    try:
        line = doc.lines[params.position.line]
        char_pos = params.position.character
        if char_pos > 0 and '.' in line[:char_pos]:
            # Find the object before the dot
            before_word = line[:char_pos - len(word) - 1] if char_pos > len(word) else ""
            obj_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*$', before_word)
            if obj_match:
                obj_name = obj_match.group(1)
                # Try to find method doc
                for class_name in METHOD_DOCS:
                    method_doc = get_method_doc(class_name, word)
                    if method_doc:
                        markdown = format_method_hover(class_name, word, method_doc)
                        return Hover(
                            contents=MarkupContent(kind=MarkupKind.Markdown, value=markdown)
                        )
    except (IndexError, AttributeError):
        pass
    
    # Check if it's a keyword
    if word in KEYWORDS:
        return Hover(
            contents=MarkupContent(
                kind=MarkupKind.Markdown,
                value=f"### {word}\n\n**Python keyword**"
            )
        )
    
    return None


# ============== Signature Help ==============
@server.feature(
    types.TEXT_DOCUMENT_SIGNATURE_HELP,
    SignatureHelpOptions(trigger_characters=['(', ','])
)
def signature_help(ls: SemanicSever, params: SignatureHelpParams) -> Optional[SignatureHelp]:
    """Provide function signature help."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    result = get_function_at_position(doc, params.position)
    
    if not result:
        return None
    
    func_name, param_index = result
    ls.log.debug(f"Signature help for: {func_name}, param index: {param_index}")
    
    func_doc = get_function_doc(func_name)
    if not func_doc:
        return None
    
    # Build parameter information
    parameters = []
    for p in func_doc.get("params", []):
        param_label = p["name"]
        if p.get("type"):
            param_label += f": {p['type']}"
        if p.get("default"):
            param_label += f" = {p['default']}"
        
        parameters.append(ParameterInformation(
            label=param_label,
            documentation=MarkupContent(
                kind=MarkupKind.Markdown,
                value=p.get("description", "")
            )
        ))
    
    signature = SignatureInformation(
        label=func_doc["signature"],
        documentation=MarkupContent(
            kind=MarkupKind.Markdown,
            value=func_doc["description"]
        ),
        parameters=parameters,
        active_parameter=min(param_index, len(parameters) - 1) if parameters else 0
    )
    
    return SignatureHelp(
        signatures=[signature],
        active_signature=0,
        active_parameter=min(param_index, len(parameters) - 1) if parameters else 0
    )


# ============== Diagnostics ==============
@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: SemanicSever, params: DidOpenTextDocumentParams):
    """Handle document open - run diagnostics."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    diagnostics = check_diagnostics(doc)
    ls.publish_diagnostics(params.text_document.uri, diagnostics)
    ls.log.debug(f"Published {len(diagnostics)} diagnostics for opened document")


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: SemanicSever, params: DidChangeTextDocumentParams):
    """Handle document change - update diagnostics."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    diagnostics = check_diagnostics(doc)
    ls.publish_diagnostics(params.text_document.uri, diagnostics)


@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: SemanicSever, params: DidSaveTextDocumentParams):
    """Handle document save - run diagnostics."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    diagnostics = check_diagnostics(doc)
    ls.publish_diagnostics(params.text_document.uri, diagnostics)
    ls.log.info(f"Document saved, {len(diagnostics)} diagnostics")


# ============== Go to Definition ==============
@server.feature(types.TEXT_DOCUMENT_DEFINITION)
def definition(ls: SemanicSever, params: DefinitionParams) -> Optional[list[Location]]:
    """Go to definition of a symbol."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    word = get_word_at_position(doc, params.position)
    
    if not word:
        return None
    
    ls.log.debug(f"Definition request for: {word}")
    
    # Find definitions in current document
    locations = find_definitions_in_doc(doc, word)
    
    if locations:
        ls.log.debug(f"Found {len(locations)} definitions")
        return locations
    
    # If it's a SageMath builtin, we can't navigate to it
    if word in FUNCTIONS or word in CLASSES:
        ls.log.debug(f"{word} is a SageMath builtin")
        return None
    
    return None


# ============== Find References ==============
@server.feature(types.TEXT_DOCUMENT_REFERENCES)
def references(ls: SemanicSever, params: ReferenceParams) -> Optional[list[Location]]:
    """Find all references to a symbol."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    word = get_word_at_position(doc, params.position)
    
    if not word:
        return None
    
    ls.log.debug(f"References request for: {word}")
    
    locations = find_references_in_doc(doc, word)
    ls.log.debug(f"Found {len(locations)} references")
    
    return locations if locations else None


# ============== Document Symbols (Outline) ==============
@server.feature(types.TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbol(ls: SemanicSever, params: DocumentSymbolParams) -> list[DocumentSymbol]:
    """Provide document symbols for outline view."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    
    # Use cached extractor or create new one
    extractor = SymbolExtractor()
    extractor.extract_symbols(doc.lines)
    symbol_extractor_cache[params.text_document.uri] = extractor
    
    symbols = extractor.to_document_symbols()
    document_symbols_cache[params.text_document.uri] = symbols
    
    ls.log.debug(f"Document symbols: found {len(symbols)} top-level symbols")
    return symbols


# ============== Folding Ranges ==============
@server.feature(types.TEXT_DOCUMENT_FOLDING_RANGE)
def folding_range(ls: SemanicSever, params: FoldingRangeParams) -> list[FoldingRange]:
    """Provide folding ranges for code folding."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ranges = []
    
    # Track blocks by indentation
    block_stack = []  # (start_line, indent_level, kind)
    
    for i, line in enumerate(doc.lines):
        stripped = line.rstrip()
        if not stripped:
            continue
        
        indent = len(line) - len(line.lstrip())
        
        # Close blocks that have ended
        while block_stack and indent <= block_stack[-1][1] and stripped and not stripped.startswith('#'):
            start_line, _, kind = block_stack.pop()
            if i - start_line > 1:  # Only fold if more than 1 line
                ranges.append(FoldingRange(
                    start_line=start_line,
                    end_line=i - 1,
                    kind=kind
                ))
        
        # Check for new blocks
        if stripped.startswith('def ') or stripped.startswith('async def '):
            block_stack.append((i, indent, FoldingRangeKind.Region))
        elif stripped.startswith('class '):
            block_stack.append((i, indent, FoldingRangeKind.Region))
        elif stripped.startswith('if ') or stripped.startswith('elif ') or stripped.startswith('else:'):
            block_stack.append((i, indent, FoldingRangeKind.Region))
        elif stripped.startswith('for ') or stripped.startswith('while '):
            block_stack.append((i, indent, FoldingRangeKind.Region))
        elif stripped.startswith('try:') or stripped.startswith('except') or stripped.startswith('finally:'):
            block_stack.append((i, indent, FoldingRangeKind.Region))
        elif stripped.startswith('with '):
            block_stack.append((i, indent, FoldingRangeKind.Region))
        elif stripped.startswith('#') and i + 1 < len(doc.lines) and doc.lines[i + 1].strip().startswith('#'):
            # Comment block
            comment_end = i
            for j in range(i + 1, len(doc.lines)):
                if doc.lines[j].strip().startswith('#'):
                    comment_end = j
                else:
                    break
            if comment_end > i:
                ranges.append(FoldingRange(
                    start_line=i,
                    end_line=comment_end,
                    kind=FoldingRangeKind.Comment
                ))
        elif '"""' in stripped or "'''" in stripped:
            # Docstring/multiline string
            quote = '"""' if '"""' in stripped else "'''"
            if stripped.count(quote) == 1:  # Opening quote only
                for j in range(i + 1, len(doc.lines)):
                    if quote in doc.lines[j]:
                        ranges.append(FoldingRange(
                            start_line=i,
                            end_line=j,
                            kind=FoldingRangeKind.Region
                        ))
                        break
    
    # Close remaining blocks
    last_line = len(doc.lines) - 1
    while block_stack:
        start_line, _, kind = block_stack.pop()
        if last_line - start_line > 1:
            ranges.append(FoldingRange(
                start_line=start_line,
                end_line=last_line,
                kind=kind
            ))
    
    ls.log.debug(f"Folding ranges: found {len(ranges)} ranges")
    return ranges


# ============== Code Actions ==============
@server.feature(
    types.TEXT_DOCUMENT_CODE_ACTION,
    CodeActionOptions(code_action_kinds=[
        CodeActionKind.QuickFix,
        CodeActionKind.Source,
        CodeActionKind.Refactor
    ])
)
def code_action(ls: SemanicSever, params: CodeActionParams) -> list[CodeAction]:
    """Provide code actions (quick fixes, refactoring)."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    
    actions = code_action_provider.get_code_actions(
        uri=params.text_document.uri,
        doc_range=params.range,
        diagnostics=params.context.diagnostics,
        lines=doc.lines,
        version=doc.version
    )
    
    ls.log.debug(f"Code actions: returning {len(actions)} actions")
    return actions


# ============== Rename Symbol ==============
@server.feature(types.TEXT_DOCUMENT_PREPARE_RENAME)
def prepare_rename(ls: SemanicSever, params: PrepareRenameParams) -> Optional[Range]:
    """Prepare for rename - validate and return range."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    word = get_word_at_position(doc, params.position)
    
    if not word:
        return None
    
    # Don't allow renaming keywords or builtins
    if word in KEYWORDS or word in FUNCTIONS or word in CLASSES:
        ls.log.debug(f"Cannot rename builtin/keyword: {word}")
        return None
    
    # Find the word range
    try:
        line = doc.lines[params.position.line]
        start = params.position.character
        end = params.position.character
        
        while start > 0 and (line[start-1].isalnum() or line[start-1] == '_'):
            start -= 1
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        
        return Range(
            start=Position(line=params.position.line, character=start),
            end=Position(line=params.position.line, character=end)
        )
    except (IndexError, AttributeError):
        return None


@server.feature(types.TEXT_DOCUMENT_RENAME)
def rename(ls: SemanicSever, params: RenameParams) -> Optional[WorkspaceEdit]:
    """Rename a symbol throughout the document."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    word = get_word_at_position(doc, params.position)
    
    if not word:
        return None
    
    new_name = params.new_name
    
    # Validate new name
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', new_name):
        ls.log.warning(f"Invalid identifier: {new_name}")
        return None
    
    # Find all references
    locations = find_references_in_doc(doc, word)
    
    if not locations:
        return None
    
    # Create text edits
    edits = []
    for loc in locations:
        edits.append(TextEdit(
            range=loc.range,
            new_text=new_name
        ))
    
    ls.log.info(f"Renaming '{word}' to '{new_name}' in {len(edits)} locations")
    
    return WorkspaceEdit(
        document_changes=[
            TextDocumentEdit(
                text_document=OptionalVersionedTextDocumentIdentifier(
                    uri=params.text_document.uri,
                    version=doc.version
                ),
                edits=edits
            )
        ]
    )


# ============== Inlay Hints ==============
@server.feature(types.TEXT_DOCUMENT_INLAY_HINT)
def inlay_hint(ls: SemanicSever, params: InlayHintParams) -> list[InlayHint]:
    """Provide inlay hints for type information."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    hints = []
    
    # Get cached symbol extractor or create new one
    if params.text_document.uri in symbol_extractor_cache:
        extractor = symbol_extractor_cache[params.text_document.uri]
    else:
        extractor = SymbolExtractor()
        extractor.extract_symbols(doc.lines)
        symbol_extractor_cache[params.text_document.uri] = extractor
    
    # Add type hints for variables with inferred types
    for sym in extractor.symbols:
        if sym.inferred_type and sym.line >= params.range.start.line and sym.line <= params.range.end.line:
            # Find the end of variable name on the line
            try:
                line = doc.lines[sym.line]
                var_end = line.find(sym.name) + len(sym.name)
                if var_end > 0 and sym.inferred_type not in ['', None]:
                    hints.append(InlayHint(
                        position=Position(line=sym.line, character=var_end),
                        label=f": {sym.inferred_type}",
                        kind=InlayHintKind.Type,
                        padding_left=False,
                        padding_right=True
                    ))
            except (IndexError, AttributeError):
                pass
    
    return hints


# ============== Enhanced Completion with User Symbols ==============
def get_user_completions(doc, partial: str) -> list[CompletionItem]:
    """Get completion items from user-defined symbols in the document."""
    extractor = SymbolExtractor()
    extractor.extract_symbols(doc.lines)
    
    items = []
    partial_lower = partial.lower() if partial else ""
    
    for sym in extractor.symbols:
        if not partial_lower or sym.name.lower().startswith(partial_lower):
            kind = CompletionItemKind.Variable
            insert_text = sym.name
            
            if sym.kind == SymbolKind.Function:
                kind = CompletionItemKind.Function
                insert_text = f"{sym.name}("
            elif sym.kind == SymbolKind.Class:
                kind = CompletionItemKind.Class
                insert_text = sym.name
            
            doc_content = ""
            if sym.docstring:
                doc_content = sym.docstring
            elif sym.signature:
                doc_content = f"```python\n{sym.signature}\n```"
            elif sym.inferred_type:
                doc_content = f"Type: `{sym.inferred_type}`"
            
            items.append(CompletionItem(
                label=sym.name,
                kind=kind,
                detail=sym.detail or "(user-defined)",
                documentation=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=doc_content
                ) if doc_content else None,
                insert_text=insert_text,
                sort_text=f"0_{sym.name}"  # User symbols appear first
            ))
    
    return items


# ============== Main ==============
if __name__ == "__main__":
    server.start_io()
