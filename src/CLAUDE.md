# src/ - 扩展入口模块

[根目录](../CLAUDE.md) > **src**

---

## 模块职责

src/ 是 VS Code 扩展的主入口模块，负责：

1. **扩展激活与停用**：实现 `activate()` 和 `deactivate()` 函数
2. **命令注册**：注册所有用户可调用的命令
3. **LSP 客户端管理**：启动、停止、重启 Language Server
4. **Conda 环境管理**：获取和选择 Conda 环境
5. **终端集成**：创建和管理 SageMath 执行终端
6. **状态栏 UI**：显示 Conda 环境选择按钮

---

## 入口与启动

### 主文件: `extension.ts`

这是扩展的唯一入口点，由 `package.json` 的 `main` 字段指定：

```json
{
  "main": "./out/extension.js"
}
```

编译后输出到 `out/extension.js` (从 `extension.ts` 编译)。

### activate() 函数流程

```typescript
export function activate(context: vscode.ExtensionContext) {
  // 1. 注册 runSageMath 命令
  // 2. 注册 selectCondaEnv 命令
  // 3. 检查是否启用 LSP
  // 4. 如果启用，检查 envLSP 虚拟环境
  // 5. 创建虚拟环境 (如不存在) 并安装依赖
  // 6. 启动 LSP 服务器
  // 7. 注册 restartLSP 命令
  // 8. 创建状态栏按钮
}
```

### deactivate() 函数

```typescript
export function deactivate(): Thenable<void> | undefined {
  if (!client) {
    return undefined;
  }
  return client.stop();
}
```

---

## 对外接口

### 注册的命令

| 命令 ID | 标题 | 功能 | 快捷键 |
|---------|------|------|--------|
| `sagemath-for-vscode.runSageMath` | Run SageMath File | 运行当前 .sage 文件 | F5 |
| `sagemath-for-vscode.restartLSP` | Restart SageMath LSP | 重启 LSP 服务器 | - |
| `sagemath-for-vscode.selectCondaEnv` | Select Conda Environment | 选择 Conda 环境 | - |

### 状态栏项

- **Conda 环境按钮**:
  - 图标: `$(terminal)`
  - 文本: "Select Conda Env"
  - 位置: 右侧状态栏
  - 显示条件: 当打开 .sage 文件时

---

## 关键依赖与配置

### NPM 依赖

```json
{
  "dependencies": {
    "vscode-languageclient": "^9.0.1"
  },
  "devDependencies": {
    "@types/node": "^24.0.1",
    "@types/vscode": "^1.100.0",
    "typescript": "~5.3.0"
  }
}
```

### VS Code API 使用

- `vscode.commands`: 命令注册
- `vscode.window`: UI 交互 (终端、消息、快速选择)
- `vscode.workspace`: 配置访问
- `vscode-languageclient`: LSP 客户端

### 配置项

扩展读取以下配置 (来自 `package.json`):

- `sagemath-for-vscode.sage.path`: SageMath 可执行文件路径
- `sagemath-for-vscode.sage.condaEnvPath`: Conda 环境路径
- `sagemath-for-vscode.LSP.useSageMathLSP`: 是否启用 LSP
- `sagemath-for-vscode.LSP.LSPLogLevel`: LSP 日志级别

---

## 数据模型

### LSP 客户端

```typescript
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind,
    State as ClientState
} from 'vscode-languageclient/node';

let client: LanguageClient;
```

**Server Options**:
```typescript
const serverOptions: ServerOptions = {
    command: pythonPath,  // envLSP/bin/python
    args: [serverModule], // src/server/lsp.py
    transport: TransportKind.stdio
};
```

**Client Options**:
```typescript
const clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: 'file', language: 'sagemath' }]
};
```

---

## 核心函数说明

### runSageMath 命令

**功能**: 在终端中运行当前 SageMath 文件

**流程**:
1. 检查是否有活动编辑器
2. 保存当前文件
3. 读取配置 (sage.path, condaEnvPath)
4. 查找或创建终端
5. 如果配置了 Conda 环境，激活它
6. 执行命令: `cd '<dir>' && sage '<file>.sage'; rm -f '<file>.sage.py'`

**特点**:
- 自动清理 `.sage.py` 中间文件
- 支持多个 Conda 环境并行使用
- 每个环境有独立的终端

### getCondaEnvs()

**功能**: 获取系统中所有 Conda 环境

**实现**:
```bash
conda env list --json
```

**返回**: `Promise<{ name: string; path: string }[]>`

### selectCondaEnv 命令

**功能**: 让用户选择 Conda 环境并更新配置

**流程**:
1. 调用 `getCondaEnvs()` 获取环境列表
2. 显示快速选择面板
3. 用户选择后更新 `sagemath-for-vscode.sage.condaEnvPath`
4. 显示确认消息

### createEnvLSP()

**功能**: 为 LSP 创建 Python 虚拟环境

**命令**:
```bash
<sage-python> -m venv <envLSPpath>
```

**特点**:
- 使用 `sage -python` 确保与 SageMath 兼容
- 需要先选择 Conda 环境
- 创建后自动安装依赖

### installRequirements()

**功能**: 在虚拟环境中安装 Python 依赖

**命令**:
```bash
<envLSP>/bin/pip install -r <requirementsPath>
```

### startLSP()

**功能**: 启动 SageMath Language Server

**流程**:
1. 创建 LanguageClient 实例
2. 配置服务器选项 (Python 解释器 + lsp.py)
3. 配置客户端选项 (只处理 .sage 文件)
4. 启动客户端
5. 发送初始日志级别配置
6. 监听配置变化，实时更新日志级别

---

## 测试与质量

### 当前状态
- ❌ 无单元测试
- ❌ 无集成测试
- ✅ 手动测试 (F5 调试)

### 测试建议

1. **命令测试**:
   - 测试 runSageMath 在各种情况下的行为
   - 测试 Conda 环境切换
   - 测试 LSP 启动和重启

2. **边界情况**:
   - 没有打开编辑器时运行命令
   - sage 路径不存在
   - Conda 未安装
   - 网络问题导致依赖安装失败

3. **建议工具**:
   - `@vscode/test-electron`: VS Code 扩展测试框架
   - Mocha 或 Jest: 测试运行器

---

## 常见问题 (FAQ)

### Q1: LSP 服务器启动失败？
**A**: 检查以下几点：
- 是否选择了 Conda 环境？
- SageMath 是否正确安装？
- `src/server/envLSP/` 是否创建成功？
- 查看 LSP 日志 (设置为 debug 级别)

### Q2: 运行 SageMath 文件后终端无输出？
**A**:
- 确认 `sagemath-for-vscode.sage.path` 配置正确
- 检查终端是否正确激活了 Conda 环境
- 手动在终端运行 sage 命令测试

### Q3: 语义高亮不工作？
**A**:
- 确认 `sagemath-for-vscode.LSP.useSageMathLSP` 为 true
- 重启 VS Code (LSP 配置更改需要重启)
- 检查 LSP 日志是否有错误

### Q4: 如何调试扩展？
**A**:
1. 按 F5 启动扩展开发主机
2. 在新窗口中打开 .sage 文件
3. 使用调试器在 extension.ts 中设置断点
4. 查看 "输出" 面板中的 "Extension Host" 频道

---

## 相关文件清单

```
src/
├── extension.ts          # 扩展主入口 (279 行)
└── server/              # LSP 服务器 (见 server/CLAUDE.md)
    ├── lsp.py            # LSP 协议处理
    ├── utils.py          # 词法和语义分析
    ├── predefinition.py  # SageMath 标准库定义
    ├── requirements.txt  # Python 依赖
    └── envLSP/           # 虚拟环境 (自动创建，gitignore)
```

---

## 开发指南

### 添加新命令

1. 在 `package.json` 中声明：
```json
{
  "contributes": {
    "commands": [{
      "command": "sagemath-for-vscode.yourCommand",
      "title": "Your Command Title"
    }]
  }
}
```

2. 在 `extension.ts` 中注册：
```typescript
let yourCommand = vscode.commands.registerCommand(
  'sagemath-for-vscode.yourCommand',
  async () => {
    // 实现逻辑
  }
);
context.subscriptions.push(yourCommand);
```

### 修改 LSP 启动逻辑

LSP 启动流程在 `activate()` 函数的后半部分：

```typescript
// 检查配置
const useLSP = vscode.workspace.getConfiguration(...)
  .get<boolean>('useSageMathLSP', true);

if (useLSP) {
  // 检查 venv
  if (!existsSync(envLSPpath)) {
    await createEnvLSP(envLSPpath, requirementsPath);
  }
  // 启动 LSP
  startLSP(envLSPpath);
}
```

### 监听配置变化

```typescript
context.subscriptions.push(
  vscode.workspace.onDidChangeConfiguration((event) => {
    if (event.affectsConfiguration('your.config.key')) {
      // 处理配置变化
    }
  })
);
```

---

## 变更记录 (Changelog)

### 2026-01-28 22:12:01
- 初始化 src 模块文档
- 整理命令和函数说明
- 添加开发指南
