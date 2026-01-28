# src/server/ - SageMath LSP 服务器模块

[根目录](../../CLAUDE.md) > [src](../) > **server**

---

## 模块职责

src/server/ 是 SageMath Language Server 的实现模块，负责：

1. **LSP 协议处理**：响应 VS Code 客户端的 LSP 请求
2. **词法分析**：将 SageMath 代码分解为 Token 流
3. **语义分类**：识别并分类函数、类、方法、变量、常量等
4. **标准库定义**：维护 SageMath 内置类型和函数列表
5. **日志系统**：提供可配置的日志输出

---

## 入口与启动

### 主文件: `lsp.py`

LSP 服务器的入口点，由 VS Code 扩展启动：

```bash
<envLSP>/bin/python lsp.py
```

### 服务器初始化

```python
from utils import SemanicSever

server = SemanicSever(name="sagemath-lsp", version="1.1.3")

@server.feature(types.INITIALIZE)
def initialize(ls: SemanicSever, params: InitializeParams):
    ls.log_level = "info"
    ls.log = Logging(ls.show_message_log, ls.log_level)
    ls.log.info("SageMath Language Server initialized")
```

### 启动流程

```
1. VS Code 扩展调用 startLSP()
2. 使用 stdio 启动 Python 子进程
3. lsp.py 创建 LanguageServer 实例
4. 注册 LSP 特性 (INITIALIZE, TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL)
5. 调用 server.start_io() 开始监听
```

---

## 对外接口

### LSP 特性

| LSP 方法 | 功能 | 实现函数 |
|---------|------|---------|
| `initialize` | 服务器初始化 | `initialize()` |
| `textDocument/semanticTokens/full` | 语义 Token 请求 | `semantic_tokens()` |
| `sagemath/loglevel` (自定义) | 动态设置日志级别 | `reload_config()` |

### 数据流

```
VS Code → LSP Client → lsp.py
  ↓
semantic_tokens()
  ↓
utils.SemanicSever.parse()
  ├─ doc_to_tokens() - 词法分析
  └─ classify_tokens() - 语义分类
  ↓
返回 SemanticTokens(data=[...])
```

---

## 关键依赖与配置

### Python 依赖 (requirements.txt)

```
pygls==1.3.1
```

**pygls**: Python Language Server 库，提供：
- `LanguageServer` 类
- `@server.feature()` 装饰器
- LSP 类型定义 (`lsprotocol.types`)

### 模块结构

```
server/
├── lsp.py            # LSP 协议处理 (61 行)
├── utils.py          # 词法/语义分析 (379 行)
├── predefinition.py  # SageMath 标准库 (28 行)
├── requirements.txt  # 依赖声明
└── envLSP/           # 虚拟环境 (自动创建)
```

---

## 数据模型

### Token 类型 (utils.py)

```python
@attrs.define
class Token:
    line: int           # 与上一个 Token 的行差
    offset: int         # 与上一个 Token 的列差
    text: str           # Token 文本
    tok_type: str       # 类型: class, function, variable, method 等
    tok_modifiers: list[str]  # 修饰符: readonly, declaration 等
```

### 语义 Token 类型 (predefinition.py)

```python
TOKEN_TYPES = [
    "namespace", "type", "class", "function", "variable",
    "parameter", "property", "method", "keyword", "modifier",
    "operator", "string", "number", "comment"
]

TOKEN_MODIFIERS = [
    "declaration", "definition", "readonly", "static",
    "deprecated", "defaultLibrary"
]
```

### SageMath 标准库 (predefinition.py)

**预定义函数**:
```python
FUNCTIONS = {
    "GCD", "crt", "diagonal_matrix", "block_matrix",
    "identity_matrix", "zero_matrix", "random_matrix"
}
```

**预定义类**:
```python
CLASSES = {
    "ZZ": {...},        # 整数环
    "QQ": {...},        # 有理数域
    "RR": {...},        # 实数域
    "CC": {...},        # 复数域
    "Zmod": {...},      # 模整数
    "GF": {...},        # 有限域
    "PolynomialRing": {...},
    "Ideal": {"methods": ["groebner_basis"], ...},
    "Matrix": {"methods": ["nrows", "ncols", "det", ...], ...},
    "vector": {...},
    "var": {...}
}
```

---

## 核心算法

### 1. 词法分析 (doc_to_tokens)

**正则表达式模式**:
```python
SYMBOL = re.compile(r"[A-Za-z_]\w*")
NUMBER = re.compile(r"(\d+(\.\d+)?[eE][-+]?\d+)|(\d+(\.\d+)?)|...")
OP = re.compile(r"(//|\^\^|==|!=|<=|>=|->|[-+*/%=<>.,:;\(\)\[\]{}\^\|\&])")
SPACE = re.compile(r"\s+")
COMMENT = re.compile(r"#.*$")
BLOCK_STRING_BEGIN = re.compile(r"('''|\"\"\").*$")
BLOCK_STRING_END = re.compile(r".*('''|\"\"\")")
LINE_STRING = re.compile(r"('(.*?)')|('''(.*?)''')|(\"(.*?)\")|(\"\"\"(.*?)\"\"\")")
```

**分词策略** (优先级从高到低):
1. 空格 - 跳过
2. 注释 - 跳过
3. 符号 (SYMBOL) - 提取标识符
4. 运算符 (OP) - 提取操作符
5. 数字 - 跳过
6. 块字符串 - 跳过
7. 行字符串 - 跳过
8. 其他字符 - 报错并跳过

### 2. 语义分类 (classify_tokens)

**识别规则**:

| 模式 | 识别结果 | 示例 |
|------|---------|------|
| `class` 后的标识符 | 类定义 | `class MyClass:` |
| `def` + `self` + `.` | 方法定义 | `def myMethod(self):` |
| `def` | 函数定义 | `def myFunc():` |
| `from` + `.` | 导入的类 | `from sage.all import Matrix` |
| `import` | 导入的模块 | `import numpy as np` |
| `for` + `in` | 循环变量 | `for i in range(10):` |
| `self.` + `=` | 属性定义 | `self.x = value` |
| `R.<x> =` | 多项式环变量 | `R.<x> = PolynomialRing(QQ)` |
| `=` 左侧 | 变量定义 | `a = 10` |
| 全大写变量 | 常量 | `MAX_SIZE = 100` |

**动态维护的数据结构**:
```python
function_names = set()        # 已知函数名
class_names = dict()          # 已知类及其成员
variable_names = dict()       # 已知变量及其类型
const_names = set()           # 已知常量
```

### 3. LSP Token 编码

**编码格式** (每个 Token 5 个整数):
```python
data.extend([
    token.line,                     # Δ 行号
    token.offset,                   # Δ 列号
    len(token.text),                # Token 长度
    TOKEN_TYPES_DIC[token.tok_type], # 类型索引
    modifier_bitmask                # 修饰符位掩码
])
```

**示例**:
```
Token: line=0, offset=0, text="Matrix", type="class", modifiers=[]
编码: [0, 0, 6, 2, 0]
```

---

## 日志系统

### Logging 类 (utils.py)

**日志级别**:
```python
PRIORITIES = {
    "debug": 1,
    "info": 2,
    "warning": 3,
    "error": 4
}
```

**使用方式**:
```python
ls.log.debug("Splitting document into tokens...")
ls.log.info("SageMath Language Server initialized")
ls.log.warning("Invalid token type or modifiers")
ls.log.error("Infinite loop detected")
```

**动态配置**:
```python
@server.feature('sagemath/loglevel')
def reload_config(ls: SemanicSever, params):
    ls.log_level = params.logLevel
    ls.log = Logging(ls.show_message_log, ls.log_level)
```

---

## 测试与质量

### 当前状态
- ❌ 无单元测试
- ❌ 无集成测试
- ✅ 通过 VS Code 手动测试

### 测试建议

1. **词法分析测试**:
```python
def test_doc_to_tokens():
    doc = TextDocument("def foo():\n    return 1", uri="test.sage")
    tokens = server.doc_to_tokens(doc)
    assert tokens[0].text == "def"
    assert tokens[1].text == "foo"
```

2. **语义分类测试**:
```python
def test_classify_class_def():
    tokens = [Token(0, 0, "class"), Token(0, 6, "MyClass"), ...]
    classify_tokens(tokens)
    assert tokens[1].tok_type == "class"
```

3. **边界情况**:
   - 空文件
   - 只有注释的文件
   - 嵌套类定义
   - 多行字符串
   - 连续运算符

4. **建议工具**:
   - pytest: Python 测试框架
   - unittest: 标准库测试框架

---

## 常见问题 (FAQ)

### Q1: 如何添加新的 SageMath 类型高亮？
**A**: 编辑 `predefinition.py`:
```python
CLASSES = {
    "NewType": {
        "methods": ["method1", "method2"],
        "properties": {"prop1": "Type1", "prop2": "Type2"}
    }
}
```

### Q2: 为什么某些变量没有被高亮？
**A**: 语义分析的限制：
- 不支持多行链式调用 (`a.b.c()`)
- 变量类型推断有限
- 需要在同一行内定义

### Q3: 如何调试 LSP 服务器？
**A**:
1. 在 VS Code 设置中将 `sagemath-for-vscode.LSP.LSPLogLevel` 设为 `debug`
2. 查看 "输出" 面板中的 "SageMath Language Server" 频道
3. 或在 `lsp.py` 中添加 `print()` 语句 (输出到终端)

### Q4: 为什么我的自定义函数没有被高亮为 function？
**A**: 当前只高亮：
- 预定义的 SageMath 函数 (`FUNCTIONS` 集合)
- 通过 `def` 定义的函数
- 如果是你自己的函数，确保在代码中用 `def` 定义

---

## 开发指南

### 添加新的 LSP 特性

```python
from lsprotocol import types

@server.feature(types.TEXT_DOCUMENT_COMPLETION)
def completion(ls: SemanicSever, params: CompletionParams):
    """实现代码补全"""
    return CompletionList(is_incomplete=False, items=[...])
```

### 修改词法规则

编辑 `utils.py` 中的正则表达式：

```python
# 添加新的运算符
OP = re.compile(r"(//|\^\w+|...)"  # 添加新模式

# 修改识别顺序
elif (match := NEW_PATTERN.match(line)) is not None:
    add_token("new_type")
```

### 优化语义分类

在 `classify_tokens()` 中添加新的识别模式：

```python
# 示例: 识别装饰器
elif token.text == "@" and i + 1 < len(tokens):
    next_token = tokens[i + 1]
    next_token.tok_type = "function"
    next_token.tok_modifiers.append("declaration")
```

---

## 性能考虑

### 当前实现
- **时间复杂度**: O(n) 其中 n 是字符数
- **内存**: 所有 Token 存储在内存中
- **触发**: 每次文档变更时完整重新分析

### 优化建议
1. **增量分析**: 只重新分析变更的行
2. **缓存**: 缓存已分析的 AST
3. **懒加载**: 延迟加载标准库定义
4. **多线程**: 使用异步处理大文件

---

## 相关文件清单

```
server/
├── lsp.py               # LSP 协议处理 (61 行)
│   ├── server 实例
│   ├── initialize()
│   ├── semantic_tokens()
│   └── reload_config()
│
├── utils.py             # 词法/语义分析 (379 行)
│   ├── Logging 类
│   ├── Token 类
│   ├── SemanicSever 类
│   ├── 正则表达式定义
│   ├── doc_to_tokens()
│   └── classify_tokens()
│
├── predefinition.py     # SageMath 标准库 (28 行)
│   ├── TOKEN_TYPES
│   ├── TOKEN_MODIFIERS
│   ├── KEYWORDS
│   ├── FUNCTIONS
│   └── CLASSES
│
└── requirements.txt     # Python 依赖
    └── pygls==1.3.1
```

---

## 变更记录 (Changelog)

### 2026-01-28 22:12:01
- 初始化 server 模块文档
- 整理词法和语义算法说明
- 添加开发指南
