# SageMath For VScode

![Release](https://img.shields.io/github/v/release/SeanDictionary/SageMath-for-VScode) ![Platform](https://img.shields.io/badge/platform-Linux-green) ![License](https://img.shields.io/github/license/SeanDictionary/SageMath-for-VScode) ![GitHub repo size](https://img.shields.io/github/repo-size/SeanDictionary/SageMath-for-VScode) ![GitHub last commit](https://img.shields.io/github/last-commit/SeanDictionary/SageMath-for-VScode) ![Python](https://img.shields.io/badge/python-3.10%2B-blue)

<div align="center"><a href="../README.md">English</a> | 中文</div>

---

## 简介

这是一个为 [SageMath](https://www.sagemath.org/) 在 VScode 上 提供语法高亮、代码运行等功能的扩展插件。

我本来是想是打造一个功能完整的 SageMath 扩展，特别是对 LSP（语言服务器协议）的支持。但是显然，我太废物了，搞定这个还是太困难了，我会慢慢完善的，所以有好的建议欢迎提出，也欢迎参与贡献。

## 功能特性

-   SageMath 代码语法高亮
-   支持部分基础的 SageMath 代码语义高亮（但是有一些已知问题，查看[问题清单](./SemanticHighlighting-zh-CN.md)了解如何规避这些问题）
-   支持 F5、命令面板和按钮运行 SageMath 文件
-   支持快捷键进行行注释和块注释
-   支持 conda 环境切换
-   语义高亮依赖根据 SageMath 标准库写的 `perdefinition.py`，你可以自己修改这个文件来添加更多的语义高亮支持

## 更新日志

详见 [CHANGELOG.md](../CHANGELOG.md)。

## 使用方法

这个插件**已经**在 VScode 插件市场发布，你可以选择从 Github 或者 VScode 插件市场安装。

### 从 GitHub 安装

1. 前往 [Releases 页面](https://github.com/SeanDictionary/SageMath-for-VScode/releases) 下载最新的预发布版或正式版本包含的 `.vsix` 文件
2. 将下载的 `.vsix` 文件拖入 Visual Studio Code 窗口，或者使用命令面板（`Ctrl+Shift+P`）输入 `Extensions: Install from VSIX...`，然后选择下载的 `.vsix` 文件。

### 从 VScode Marketplace 安装

1. 打开 Visual Studio Code
2. 点击侧边栏的扩展图标或按 `Ctrl+Shift+X` 进入扩展视图
3. 搜索 "SageMath for VScode"
4. 点击 SeanDictionary 发布的 "SageMath for VScode" 扩展后点“安装”
5. 安装完成后，可能需要重载窗口或重启 VS Code
6. 打开 `.sage` 后缀的 SageMath 文件即可使用扩展

## 参与贡献

欢迎通过 Fork 本仓库并提交 PR 的方式参与开发，也可以通过 issue 报告问题或提出新功能建议。

## 协议

本项目使用 AGPL-3.0 协议，详情见 [LICENSE](../LICENSE) 文件。
