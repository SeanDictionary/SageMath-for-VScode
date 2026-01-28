# How LSP Client Works

## 1. LSP Client Initialization

The LSP client is initialized in the `startLSP()` function (`src/extension.ts:202-241`) when the extension activates and `sagemath-for-vscode.LSP.useSageMathLSP` is true.

**Server Options Configuration:**
```typescript
const serverOptions: ServerOptions = {
  command: pythonPath,  // Path to envLSP/bin/python
  args: [serverModule], // Path to src/server/lsp.py
  transport: TransportKind.stdio
};
```

**Client Options Configuration:**
```typescript
const clientOptions: LanguageClientOptions = {
  documentSelector: [{ scheme: 'file', language: 'sagemath' }]
};
```

**Client Creation:**
```typescript
client = new LanguageClient(
  'sagemath-lsp',
  'SageMath Language Server',
  serverOptions,
  clientOptions
);
```

## 2. LSP Server Startup

The server process starts with `client.start()` (`src/extension.ts:222-229`):

- Spawns Python subprocess executing `src/server/lsp.py`
- Establishes stdio communication channel
- Sends `initialize` request to server
- Server responds with capabilities (semantic tokens provider)
- Client sends initial log level via custom `sagemath/loglevel` notification

## 3. Request-Response Communication

**Semantic Tokens Request Flow:**
- User opens or edits `.sage` file
- VS Code sends `textDocument/semanticTokens/full` request to client
- Client forwards request to LSP server via stdio
- Server's `semantic_tokens()` handler processes document (`src/server/lsp.py:35-56`)
  - Calls `ls.parse(doc)` which tokenizes and classifies code
  - Encodes tokens into LSP format (line delta, offset delta, length, type, modifiers)
  - Returns `SemanticTokens(data=[...])` array
- Client receives response and forwards to VS Code
- VS Code renders semantic highlighting in editor

## 4. Dynamic Configuration

LSP server log level can be changed without restart (`src/extension.ts:232-240`):

- Extension watches `sagemath-for-vscode.LSP.LSPLogLevel` configuration changes
- Sends custom `sagemath/loglevel` notification to server
- Server's `reload_config()` handler updates log level (`src/server/lsp.py:16-20`)
- New log level takes effect immediately

## 5. Client Lifecycle Management

**Restart Handler** (`src/extension.ts:306-322`):
- Checks if client is running (`client.state === ClientState.Running`)
- Stops client with `await client.stop()`
- Restarts with `await client.start()`
- Shows success/error message

**Deactivation** (`src/extension.ts:350-355`):
- Extension's `deactivate()` function calls `client.stop()`
- Gracefully terminates Python subprocess
- Cleans up resources

## 6. Communication Protocol

**Transport:** stdio (standard input/output)
**Format:** JSON-RPC 2.0 messages (handled by vscode-languageclient library)
**Server Implementation:** Python pygls framework (`src/server/lsp.py`)

**Key LSP Methods Implemented:**
- `initialize` - Server initialization (`src/server/lsp.py:26-30`)
- `textDocument/semanticTokens/full` - Semantic highlighting (`src/server/lsp.py:34-56`)
- `sagemath/loglevel` - Custom notification for log configuration (`src/server/lsp.py:16-20`)
