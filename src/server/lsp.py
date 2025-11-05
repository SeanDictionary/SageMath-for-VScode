from functools import reduce
from lsprotocol.types import (
    SemanticTokens, SemanticTokensParams, SemanticTokensLegend, InitializeParams
)
from lsprotocol import types
from utils import Logging, SemanicSever
from predefinition import TOKEN_TYPES, TOKEN_MODIFIERS

TOKEN_TYPES_DIC = {s: i for i, s in enumerate(TOKEN_TYPES)}
TOKEN_MODIFIERS_DIC = {s: 2**i for i, s in enumerate(TOKEN_MODIFIERS)}

server = SemanicSever(name="sagemath-lsp", version="1.1.2")


# -----------Logging Configuration-----------
@server.feature('sagemath/loglevel')
def reload_config(ls: SemanicSever, params):
    ls.log_level = params.logLevel
    ls.log = Logging(ls.show_message_log, ls.log_level)
# -------------------------------------------

legend = SemanticTokensLegend(token_types=TOKEN_TYPES, token_modifiers=TOKEN_MODIFIERS)


# Initialize Info
@server.feature(types.INITIALIZE)
def initialize(ls: SemanicSever, params: InitializeParams):
    ls.log_level = "info"
    ls.log = Logging(ls.show_message_log, ls.log_level)
    ls.log.info("SageMath Language Server initialized")


# Semantic Tokens Feature
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

    # Debug for: send encoded tokens
    # for i in range(0,len(data),5):
    #     ls.log.debug(f"Send token: {data[i:i+5]}")

    return SemanticTokens(data=data)


if __name__ == "__main__":
    server.start_io()
