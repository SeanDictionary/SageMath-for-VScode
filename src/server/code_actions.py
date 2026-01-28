"""
Code Actions module for SageMath LSP
Provides: Quick fixes, refactoring suggestions, source actions
"""

from __future__ import annotations
import re
from typing import Optional

from lsprotocol.types import (
    CodeAction, CodeActionKind, TextEdit, WorkspaceEdit,
    Range, Position, Diagnostic, DiagnosticSeverity,
    TextDocumentEdit, OptionalVersionedTextDocumentIdentifier,
    AnnotatedTextEdit, ChangeAnnotation
)

from predefinition import FUNCTIONS, CLASSES, KEYWORDS


class CodeActionProvider:
    """Provides code actions for SageMath documents"""
    
    # Common imports for SageMath
    COMMON_IMPORTS = {
        # Functions that need specific imports
        'bytes_to_long': 'from Crypto.Util.number import bytes_to_long',
        'long_to_bytes': 'from Crypto.Util.number import long_to_bytes',
        'getRandomNBitInteger': 'from Crypto.Util.number import getRandomNBitInteger',
        'getPrime': 'from Crypto.Util.number import getPrime',
        'isPrime': 'from Crypto.Util.number import isPrime',
        # numpy
        'np': 'import numpy as np',
        'numpy': 'import numpy',
        # itertools
        'itertools': 'import itertools',
        'product': 'from itertools import product',
        'permutations': 'from itertools import permutations',
        'combinations': 'from itertools import combinations',
        # functools
        'functools': 'import functools',
        'reduce': 'from functools import reduce',
        'lru_cache': 'from functools import lru_cache',
        # collections
        'Counter': 'from collections import Counter',
        'defaultdict': 'from collections import defaultdict',
        'deque': 'from collections import deque',
        # typing
        'Optional': 'from typing import Optional',
        'List': 'from typing import List',
        'Dict': 'from typing import Dict',
        'Tuple': 'from typing import Tuple',
        # time
        'time': 'import time',
        'sleep': 'from time import sleep',
        # json
        'json': 'import json',
        # os/sys
        'os': 'import os',
        'sys': 'import sys',
        # re
        're': 'import re',
        # hashlib
        'hashlib': 'import hashlib',
        'md5': 'from hashlib import md5',
        'sha256': 'from hashlib import sha256',
        # struct
        'struct': 'import struct',
        'pack': 'from struct import pack',
        'unpack': 'from struct import unpack',
        # binascii
        'binascii': 'import binascii',
        'hexlify': 'from binascii import hexlify',
        'unhexlify': 'from binascii import unhexlify',
        # base64
        'base64': 'import base64',
        'b64encode': 'from base64 import b64encode',
        'b64decode': 'from base64 import b64decode',
    }
    
    # Similar name suggestions for typos
    SIMILAR_NAMES = {
        'matirx': 'matrix',
        'matrx': 'matrix',
        'marix': 'matrix',
        'vecor': 'vector',
        'vctor': 'vector',
        'fcator': 'factor',
        'factr': 'factor',
        'prme': 'prime',
        'pirme': 'prime',
        'gcd_': 'gcd',
        'lcm_': 'lcm',
        'xgcd_': 'xgcd',
        'intger': 'Integer',
        'integr': 'Integer',
        'ratinal': 'Rational',
        'ratoinal': 'Rational',
        'eliptic': 'EllipticCurve',
        'elliptic': 'EllipticCurve',
        'polynomialring': 'PolynomialRing',
        'polinomialring': 'PolynomialRing',
        'polyring': 'PolynomialRing',
        'finitefiled': 'GF',
        'finitefield': 'GF',
        'numberfeild': 'NumberField',
        'numberfiled': 'NumberField',
        'discret_log': 'discrete_log',
        'discretelog': 'discrete_log',
        'invese_mod': 'inverse_mod',
        'inversemod': 'inverse_mod',
        'powr_mod': 'power_mod',
        'powermod': 'power_mod',
    }
    
    def __init__(self):
        pass
    
    def get_code_actions(
        self,
        uri: str,
        doc_range: Range,
        diagnostics: list[Diagnostic],
        lines: list[str],
        version: Optional[int] = None
    ) -> list[CodeAction]:
        """Get code actions for the given range and diagnostics"""
        actions = []
        
        for diagnostic in diagnostics:
            # Handle undefined name diagnostics
            if "may not be defined" in diagnostic.message or "undefined" in diagnostic.message.lower():
                actions.extend(self._get_undefined_name_actions(uri, diagnostic, lines, version))
            
            # Handle mixed indentation
            if "Mixed tabs and spaces" in diagnostic.message:
                actions.extend(self._get_indentation_fix_actions(uri, diagnostic, lines, version))
            
            # Handle assignment in condition
            if "assignment in condition" in diagnostic.message.lower():
                actions.extend(self._get_assignment_fix_actions(uri, diagnostic, lines, version))
        
        # Add source actions (available even without diagnostics)
        actions.extend(self._get_source_actions(uri, doc_range, lines, version))
        
        return actions
    
    def _get_undefined_name_actions(
        self,
        uri: str,
        diagnostic: Diagnostic,
        lines: list[str],
        version: Optional[int]
    ) -> list[CodeAction]:
        """Get actions for undefined names"""
        actions = []
        
        # Extract the undefined name from diagnostic message
        match = re.search(r"'([^']+)'", diagnostic.message)
        if not match:
            return actions
        
        undefined_name = match.group(1)
        
        # Check if we have a common import for this name
        if undefined_name in self.COMMON_IMPORTS:
            import_statement = self.COMMON_IMPORTS[undefined_name]
            actions.append(self._create_add_import_action(
                uri, import_statement, lines, version,
                f"Add import: {import_statement}"
            ))
        
        # Check for similar names (typo correction)
        if undefined_name.lower() in self.SIMILAR_NAMES:
            correct_name = self.SIMILAR_NAMES[undefined_name.lower()]
            actions.append(self._create_replace_text_action(
                uri, diagnostic.range, correct_name, version,
                f"Did you mean '{correct_name}'?"
            ))
        
        # Check against SageMath functions for fuzzy match
        similar = self._find_similar_names(undefined_name, FUNCTIONS | set(CLASSES.keys()))
        for name in similar[:3]:  # Limit to 3 suggestions
            actions.append(self._create_replace_text_action(
                uri, diagnostic.range, name, version,
                f"Did you mean '{name}'?"
            ))
        
        return actions
    
    def _get_indentation_fix_actions(
        self,
        uri: str,
        diagnostic: Diagnostic,
        lines: list[str],
        version: Optional[int]
    ) -> list[CodeAction]:
        """Get actions for mixed indentation"""
        actions = []
        
        line_num = diagnostic.range.start.line
        if line_num >= len(lines):
            return actions
        
        line = lines[line_num]
        
        # Convert tabs to spaces (4 spaces per tab)
        fixed_line = line.expandtabs(4)
        
        actions.append(CodeAction(
            title="Convert tabs to spaces",
            kind=CodeActionKind.QuickFix,
            diagnostics=[diagnostic],
            edit=WorkspaceEdit(
                document_changes=[
                    TextDocumentEdit(
                        text_document=OptionalVersionedTextDocumentIdentifier(
                            uri=uri,
                            version=version
                        ),
                        edits=[
                            TextEdit(
                                range=Range(
                                    start=Position(line=line_num, character=0),
                                    end=Position(line=line_num, character=len(line))
                                ),
                                new_text=fixed_line.rstrip()
                            )
                        ]
                    )
                ]
            )
        ))
        
        return actions
    
    def _get_assignment_fix_actions(
        self,
        uri: str,
        diagnostic: Diagnostic,
        lines: list[str],
        version: Optional[int]
    ) -> list[CodeAction]:
        """Get actions for assignment in condition"""
        actions = []
        
        line_num = diagnostic.range.start.line
        if line_num >= len(lines):
            return actions
        
        line = lines[line_num]
        
        # Find single = and replace with ==
        # Be careful not to replace == or != or <= or >=
        fixed_line = re.sub(r'(?<![=!<>])=(?!=)', '==', line)
        
        if fixed_line != line:
            actions.append(CodeAction(
                title="Change '=' to '==' for comparison",
                kind=CodeActionKind.QuickFix,
                diagnostics=[diagnostic],
                edit=WorkspaceEdit(
                    document_changes=[
                        TextDocumentEdit(
                            text_document=OptionalVersionedTextDocumentIdentifier(
                                uri=uri,
                                version=version
                            ),
                            edits=[
                                TextEdit(
                                    range=Range(
                                        start=Position(line=line_num, character=0),
                                        end=Position(line=line_num, character=len(line))
                                    ),
                                    new_text=fixed_line.rstrip()
                                )
                            ]
                        )
                    ]
                )
            ))
        
        return actions
    
    def _get_source_actions(
        self,
        uri: str,
        doc_range: Range,
        lines: list[str],
        version: Optional[int]
    ) -> list[CodeAction]:
        """Get source actions (organize imports, add docstring, etc.)"""
        actions = []
        
        # Check if cursor is on a function definition
        line_num = doc_range.start.line
        if line_num < len(lines):
            line = lines[line_num]
            
            # Add docstring to function
            func_match = re.match(r'^(\s*)def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*:', line)
            if func_match:
                indent = func_match.group(1) or ""
                func_name = func_match.group(2)
                params = func_match.group(3)
                
                # Check if docstring already exists
                if line_num + 1 < len(lines):
                    next_line = lines[line_num + 1].strip()
                    if not (next_line.startswith('"""') or next_line.startswith("'''")):
                        docstring = self._generate_docstring(func_name, params, indent + "    ")
                        actions.append(CodeAction(
                            title="Generate docstring",
                            kind=CodeActionKind.Source,
                            edit=WorkspaceEdit(
                                document_changes=[
                                    TextDocumentEdit(
                                        text_document=OptionalVersionedTextDocumentIdentifier(
                                            uri=uri,
                                            version=version
                                        ),
                                        edits=[
                                            TextEdit(
                                                range=Range(
                                                    start=Position(line=line_num + 1, character=0),
                                                    end=Position(line=line_num + 1, character=0)
                                                ),
                                                new_text=docstring
                                            )
                                        ]
                                    )
                                ]
                            )
                        ))
        
        return actions
    
    def _create_add_import_action(
        self,
        uri: str,
        import_statement: str,
        lines: list[str],
        version: Optional[int],
        title: str
    ) -> CodeAction:
        """Create an action to add an import statement"""
        # Find the best position to add import
        insert_line = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_line = i + 1
            elif line.strip() and not line.strip().startswith('#') and insert_line > 0:
                break
        
        return CodeAction(
            title=title,
            kind=CodeActionKind.QuickFix,
            edit=WorkspaceEdit(
                document_changes=[
                    TextDocumentEdit(
                        text_document=OptionalVersionedTextDocumentIdentifier(
                            uri=uri,
                            version=version
                        ),
                        edits=[
                            TextEdit(
                                range=Range(
                                    start=Position(line=insert_line, character=0),
                                    end=Position(line=insert_line, character=0)
                                ),
                                new_text=f"{import_statement}\n"
                            )
                        ]
                    )
                ]
            )
        )
    
    def _create_replace_text_action(
        self,
        uri: str,
        range: Range,
        new_text: str,
        version: Optional[int],
        title: str
    ) -> CodeAction:
        """Create an action to replace text"""
        return CodeAction(
            title=title,
            kind=CodeActionKind.QuickFix,
            edit=WorkspaceEdit(
                document_changes=[
                    TextDocumentEdit(
                        text_document=OptionalVersionedTextDocumentIdentifier(
                            uri=uri,
                            version=version
                        ),
                        edits=[
                            TextEdit(
                                range=range,
                                new_text=new_text
                            )
                        ]
                    )
                ]
            )
        )
    
    def _find_similar_names(self, name: str, candidates: set) -> list[str]:
        """Find similar names using Levenshtein distance"""
        name_lower = name.lower()
        results = []
        
        for candidate in candidates:
            distance = self._levenshtein_distance(name_lower, candidate.lower())
            if distance <= 2:  # Allow up to 2 character difference
                results.append((distance, candidate))
        
        results.sort(key=lambda x: x[0])
        return [r[1] for r in results if r[1].lower() != name_lower]
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _generate_docstring(self, func_name: str, params: str, indent: str) -> str:
        """Generate a docstring template for a function"""
        lines = [f'{indent}"""']
        lines.append(f'{indent}Description of {func_name}.')
        lines.append(f'{indent}')
        
        # Parse parameters
        if params.strip():
            param_list = []
            for p in params.split(','):
                p = p.strip()
                if p and p != 'self':
                    # Handle type hints
                    if ':' in p:
                        param_name = p.split(':')[0].strip()
                    elif '=' in p:
                        param_name = p.split('=')[0].strip()
                    else:
                        param_name = p
                    param_list.append(param_name)
            
            if param_list:
                lines.append(f'{indent}Args:')
                for param in param_list:
                    lines.append(f'{indent}    {param}: Description.')
                lines.append(f'{indent}')
        
        lines.append(f'{indent}Returns:')
        lines.append(f'{indent}    Description of return value.')
        lines.append(f'{indent}"""')
        
        return '\n'.join(lines) + '\n'
