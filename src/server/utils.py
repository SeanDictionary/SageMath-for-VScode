from __future__ import annotations

import time
import re
from typing import Callable, Optional

import attrs
from pygls.server import LanguageServer
from pygls.workspace import TextDocument

from predefinition import FUNCTIONS, CLASSES, KEYWORDS


class Logging:
    PRIORITIES = {
        "debug": 1,
        "info": 2,
        "warning": 3,
        "error": 4
    }

    def __init__(self, function: callable, log_level: str = "info"):
        self.function = function
        self.log_level = self.PRIORITIES.get(log_level.lower(), 2)

    def _log(self, level: str, message: str):
        if self.PRIORITIES[level.lower()] >= self.log_level:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            self.function(f"{timestamp} [{level}] {message}")

    def debug(self, message: str):
        self._log("Debug", message)

    def info(self, message: str):
        self._log("Info", message)

    def warning(self, message: str):
        self._log("Warning", message)

    def error(self, message: str):
        self._log("Error", message)


# Reference from official documents
# https://pygls.readthedocs.io/en/latest/servers/examples/semantic-tokens.html

# Pre-compiled regex patterns for tokenization (module-level for performance)
SYMBOL = re.compile(r"[A-Za-z_]\w*")
NUMBER = re.compile(r"(\d+(\.\d+)?[eE][-+]?\d+)|(\d+(\.\d+)?)|0[bB][01]+|0[oO][0-7]+|0[xX][0-9a-fA-F]+")
OP = re.compile(r"(//|\^\^|==|!=|<=|>=|->|[-+*/%=<>.,:;\(\)\[\]{}\^\|\&])")
SPACE = re.compile(r"\s+")
COMMENT = re.compile(r"#.*$")
BLOCK_STRING_BEGIN = re.compile(r"('''|\"\"\").*$")
BLOCK_STRING_END = re.compile(r".*('''|\"\"\")")
LINE_STRING = re.compile(r"('(.*?)')|('''(.*?)''')|(\"(.*?)\")|(\"\"\"(.*?)\"\"\")")
MATCH_ALL_LINE = re.compile(r"^.*$")


@attrs.define
class Token:
    """Represents a semantic token with position and classification info."""
    line: int
    offset: int
    text: str

    tok_type: str = ""
    tok_modifiers: list[str] = attrs.Factory(list)

    def __str__(self) -> str:
        return f"{self.line}:{self.offset} {self.text!r} {self.tok_type} {self.tok_modifiers}"


class SemanicSever(LanguageServer):
    """Custom Language Server with semantic token parsing capabilities."""
    
    log_level: str
    log: Logging

    def __init__(self, name: str, version: str, log_level: str = "info") -> None:
        super().__init__(name=name, version=version)
        self.log_level = log_level
        self.log = Logging(self.show_message_log, log_level)

    def doc_to_tokens(self, doc: TextDocument) -> list[Token]:
        """Convert the given document into a list of tokens."""
        tokens = []

        prev_line = 0
        prev_offset = 0
        current_line = 0

        def add_token(tok_type: str = "") -> None:
            nonlocal prev_line, prev_offset, current_line, current_offset, line, match
            tokens.append(
                Token(
                    line=current_line - prev_line,
                    offset=current_offset - prev_offset,
                    text=match.group(0),
                    tok_type=tok_type,
                    tok_modifiers=[]
                )
            )
            # self.log.debug(f"Splited token: {tokens[-1]}")  # Debug for: split into tokens

            line = line[match.end():]
            prev_offset = current_offset
            prev_line = current_line
            current_offset += len(match.group(0))

        self.log.debug(f"Splitting document into tokens: {doc.uri}")

        while current_line < len(doc.lines):
            line = doc.lines[current_line]
            prev_offset = current_offset = 0
            chars_left = len(line)

            while line:
                if (match := SPACE.match(line)) is not None:
                    # Skip whitespace
                    current_offset += len(match.group(0))
                    line = line[match.end():]

                elif (match := COMMENT.match(line)) is not None:
                    # Skip
                    # add_token("comment")
                    current_offset += len(match.group(0))
                    line = line[match.end():]
                    pass

                elif (match := SYMBOL.match(line)) is not None:
                    add_token()

                elif (match := OP.match(line)) is not None:
                    add_token("operator")

                elif (match := NUMBER.match(line)) is not None:
                    # Skip
                    # add_token("number")
                    current_offset += len(match.group(0))
                    line = line[match.end():]
                    pass

                elif (match := BLOCK_STRING_BEGIN.match(line)) is not None:
                    # Skip
                    # add_token("string")
                    current_offset += len(match.group(0))
                    line = line[match.end():]
                    current_line += 1
                    while (current_line < len(doc.lines)):
                        line = doc.lines[current_line]
                        prev_offset = current_offset = 0
                        chars_left = len(line)
                        if (match := BLOCK_STRING_END.match(line)) is not None:
                            # add_token("string")
                            current_offset += len(match.group(0))
                            line = line[match.end():]
                            break
                        else:
                            match = MATCH_ALL_LINE.match(line)
                            if match:
                                current_offset += len(match.group(0))
                                line = line[match.end():]
                            current_line += 1

                elif (match := LINE_STRING.match(line)) is not None:
                    # Skip
                    # add_token("string")
                    current_offset += len(match.group(0))
                    line = line[match.end():]
                    pass

                else:
                    self.log.error(f"No match, in line&offset: {current_line}:{current_offset} {line[0]!r}")
                    current_offset += 1
                    line = line[1:]

                # Make sure we don't hit an infinite loop
                if (n := len(line)) == chars_left:
                    self.log.error(f"Inifite loop detected, in line&offset: {current_line}:{current_offset} {line!r}")
                    break
                else:
                    chars_left = n

            current_line += 1

        return tokens

    def classify_tokens(self, tokens: list[Token]) -> None:
        """Classify tokens into types and modifiers."""
        # Use shallow copy for immutable items, deep copy structure for mutable nested dicts
        function_names: set[str] = set(FUNCTIONS)
        class_names: dict[str, dict] = {k: {"methods": list(v["methods"]), "properties": dict(v["properties"])} for k, v in CLASSES.items()}
        variable_names: dict[str, str] = {}
        const_names: set[str] = set()

        for i, token in enumerate(tokens):
            # Skip tokens that are already classified
            if token.tok_type == "":

                # Highlight new defined variables and functions
                if token.text in KEYWORDS:
                    token.tok_type = ""     # Leave it to the native Python keyword syntaxes highlighting
                    if token.text == "class" and i + 1 < len(tokens) and tokens[i + 1].line == 0:
                        next_token = tokens[i + 1]
                        class_names[next_token.text] = {"methods": [], "properties": {}}
                    elif token.text == "from" and i + 1 < len(tokens):
                        tmp = 1
                        while i + tmp < len(tokens) and tokens[i + tmp].line == 0:
                            next_token = tokens[i + tmp]
                            if next_token.text != "*":
                                next_token.tok_type = "class"
                            tmp += 1
                            if i + tmp < len(tokens) and tokens[i + tmp].text == "." and tokens[i + 1].line == 0:
                                tmp += 1
                            else:
                                break
                    # ? Unable to recognize the import name is a class or a function. and the methods of the imported class can't be recognized and hightlighted.
                    elif token.text == "import" and i + 1 < len(tokens):
                        tmp = 1
                        while i + tmp < len(tokens) and tokens[i + tmp].line == 0:
                            next_token = tokens[i + tmp]
                            if next_token.text != "*":
                                next_token.tok_type = "class"
                            tmp += 1
                            if i + tmp < len(tokens) and tokens[i + tmp].text == "." and tokens[i + 1].line == 0:
                                tmp += 1
                            elif i + tmp < len(tokens) and tokens[i + tmp].text == "as" and tokens[i + 1].line == 0:
                                tmp += 1
                                if i + tmp < len(tokens) and tokens[i + tmp].line == 0:
                                    next_token = tokens[i + tmp]
                                    if next_token.text != "*":
                                        next_token.tok_type = "class"
                                break
                        if next_token.text != "*":
                            class_names[next_token.text] = {"methods": [], "properties": {}}
                    elif token.text == "def" and i + 1 < len(tokens):
                        if i + 3 < len(tokens) and tokens[i + 3].text == "self" and tokens[i + 3].line == 0:
                            next_token = tokens[i + 1]
                            next_token.tok_type = "method"
                            class_name = list(class_names.keys())[-1]
                            class_names[class_name]["methods"].append(next_token.text)
                        else:
                            next_token = tokens[i + 1]
                            function_names.add(next_token.text)

                    elif token.text == "self" and i + 2 < len(tokens):
                        if i + 4 < len(tokens) and tokens[i + 1].text == "." and tokens[i + 3].text == "=":
                            next_token = tokens[i + 2]
                            next_token.tok_type = "variable"
                            class_name = list(class_names.keys())[-1]
                            if tokens[i + 4].text in class_names and tokens[i + 4].line == 0:
                                class_names[class_name]["properties"][next_token.text] = tokens[i + 4].text
                            else:
                                class_names[class_name]["properties"][next_token.text] = ""
                        elif tokens[i + 1].text == ".":
                            next_token = tokens[i + 2]
                            class_name = list(class_names.keys())[-1]
                            if next_token.text in class_names[class_name]["methods"]:
                                next_token.tok_type = "method"
                            elif next_token.text in class_names[class_name]["properties"]:
                                next_token.tok_type = "variable"
                    # ? Unsupport highlighting variables inline for loop
                    elif token.text == "for":
                        tmp = 1
                        while i + tmp < len(tokens) and tokens[i + tmp].line == 0:
                            next_token = tokens[i + tmp]
                            if next_token.text != "in":
                                next_token.tok_type = "variable"
                                if next_token.text == next_token.text.upper():
                                    next_token.tok_modifiers.append("readonly")
                                    const_names.add(next_token.text)
                                variable_names[next_token.text] = ""
                            else:
                                break
                            tmp += 1
                            if i + tmp < len(tokens) and tokens[i + tmp].text == ",":
                                tmp += 1
                            else:
                                break


                # // Add new defined variables, but it only support for single define
                # elif i + 1 < len(tokens) and tokens[i + 1].text == "=" and tokens[i + 1].line == 0:
                #     token.tok_type = "variable"
                #     if token.text == token.text.upper():
                #         token.tok_modifiers.append("readonly")
                #         const_names.add(token.text)
                #     if i + 2 < len(tokens) and tokens[i + 2].text in class_names and tokens[i + 2].line == 0:
                #         variable_names[token.text] = tokens[i + 2].text
                #     else:
                #         variable_names[token.text] = ""


                # Special check for R.<x> = PolynomialRing(QQ)
                elif i + 2 < len(tokens) and tokens[i + 1].text == "." and tokens[i + 2].text == "<":
                    tmp = 3
                    while i + tmp < len(tokens) and tokens[i + tmp].line == 0:
                        if tokens[i + tmp].tok_type == "":
                            next_token = tokens[i + tmp]
                            next_token.tok_type = "variable"
                            variable_names[next_token.text] = ""
                            tmp += 1
                            if i + tmp < len(tokens) and tokens[i + tmp].text == ",":
                                tmp += 1
                                continue
                            elif i + tmp < len(tokens) and tokens[i + tmp].text == ">":
                                if i + tmp + 2 < len(tokens) and tokens[i + tmp + 1].text == "=":
                                    token.tok_type = "variable"
                                    if tokens[i + tmp + 2].text in class_names and tokens[i + tmp + 2].line == 0:
                                        variable_names[token.text] = tokens[i + tmp + 2].text
                                    break
                            else:
                                break
                        else:
                            break


                # ? There will be some problems while using the same name from different set, like a = a().
                # ? So pls correctly name your variables, QAQ
                elif token.text in function_names:
                    token.tok_type = "function"
                elif token.text in class_names:
                    token.tok_type = "class"
                elif token.text in variable_names:
                    token.tok_type = "variable"
                    if token.text in const_names:
                        token.tok_modifiers.append("readonly")
                    # Check if the next token is a method or property of a class
                    # ? Not support mulity-calls yet, like a.b.c(). It only support a.b or a.b()
                    if i + 2 < len(tokens) and tokens[i + 1].text == "." and tokens[i + 1].line == 0:
                        next_token = tokens[i + 2]
                        if variable_names[token.text] != "":
                            if next_token.text in class_names[variable_names[token.text]]["methods"]:
                                next_token.tok_type = "method"
                            elif next_token.text in class_names[variable_names[token.text]]["properties"]:
                                next_token.tok_type = "variable"

                # Otherwise classify tokens as no highlighted
                else:
                    token.tok_type = ""
            
            # Add new defined variables, support for multy define
            elif token.text == "=":
                tmp = 1
                tmp_variables = []
                while tmp <= i:
                    if tokens[i - tmp].tok_type not in ["keyword", "operator"]:
                        tokens[i - tmp].tok_type = "variable"
                        tmp_variables.append(tokens[i - tmp].text)
                        if tokens[i - tmp].text == tokens[i - tmp].text.upper():
                            tokens[i - tmp].tok_modifiers.append("readonly")
                            const_names.add(tokens[i - tmp].text)
                    tmp += 1
                    if tokens[i - tmp].text != ",":
                        break
                    tmp += 1
                if len(tmp_variables) == 1:
                    if i + 1 < len(tokens) and tokens[i + 1].text in class_names and tokens[i + 1].line == 0:
                        variable_names[tmp_variables[0]] = tokens[i + 1].text
                    else:
                        variable_names[tmp_variables[0]] = ""
                else:
                    # It's hard to determine the type of the variable, so just set it to empty
                    for name in tmp_variables:
                        variable_names[name] = ""

            # self.log.debug(f"Classified token: {token}")    # Debug for: classify tokens

        # self.log.debug(f"Classified class: {class_names}")
        # self.log.debug(f"Classified function: {function_names}")
        self.log.debug(f"Classified variable: {variable_names}")
        self.log.debug(f"Classified const: {const_names}")

    def parse(self, doc: TextDocument) -> list[Token]:
        """Get tokens from the document."""
        tokens = self.doc_to_tokens(doc)
        self.classify_tokens(tokens)

        return tokens


if __name__ == "__main__":
    logger = Logging(print, "warning")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
