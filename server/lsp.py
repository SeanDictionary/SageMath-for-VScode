from pygls.server import LanguageServer
from lsprotocol.types import (
    SemanticTokens, SemanticTokensParams, SemanticTokensLegend, InitializeParams
)
from lsprotocol import types
from utils import Logging

server = LanguageServer(name="sagemath-lsp", version="0.0.1")


# -----------Logging Configuration-----------
@server.feature('sagemath/loglevel')
def reload_config(ls: LanguageServer, params):
    new_log_level = params.logLevel
    ls.log_level = new_log_level
    ls.log = Logging(ls.show_message_log, ls.log_level)
# -------------------------------------------


TOKEN_TYPES = ["method", "function", "variable", "class"]
TOKEN_MODIFIERS = ["declaration"]
legend = SemanticTokensLegend(token_types=TOKEN_TYPES, token_modifiers=TOKEN_MODIFIERS)


# Initialize Info
@server.feature(types.INITIALIZE)
def initialize(ls: LanguageServer, params: InitializeParams):
    ls.log_level = "info"
    ls.log = Logging(ls.show_message_log, ls.log_level)
    ls.log.info("SageMath Language Server initialized")

# Semantic Tokens Feature
@server.feature(types.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, legend)
def semantic_tokens(ls: LanguageServer, params: SemanticTokensParams) -> SemanticTokens:
    doc = ls.workspace.get_text_document(params.text_document.uri)
    source = doc.source
    tokens = []

    for lineno, line in enumerate(source.splitlines()):
        col = line.find("helloworld")
        if col != -1:
            tokens.append((lineno, col, len("helloworld"), TOKEN_TYPES.index("function"), 0))
    ls.log.debug(f"Semantic tokens generated: {tokens}")
    return SemanticTokens(data=encode_tokens(tokens))


def encode_tokens(tokens):
    result = []
    prev_line = 0
    prev_char = 0
    for line, char, length, token_type, token_modifiers in sorted(tokens):
        delta_line = line - prev_line
        delta_start = char - prev_char if delta_line == 0 else char
        result += [delta_line, delta_start, length, token_type, token_modifiers]
        prev_line = line
        prev_char = char
    return result


if __name__ == "__main__":
    server.start_io()
