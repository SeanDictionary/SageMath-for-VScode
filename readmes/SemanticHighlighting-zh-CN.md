# 一些语义高亮显示的已知问题

这个文档列出了在语义高亮显示中已知的一些问题。如果你遇到了一些 bug，请先查看这篇文档是否已经记录。代码高亮本身并不影响运行，而且大部分的问题只要你规范书写代码基本是碰不到的，所以后续并不打算修复这些问题（其实是我太菜了），除非未来哪天打算全面重构高亮部分，才会考虑修复。

<div align="center"><a href="./SemanticHighlighting-en.md">English</a> | 中文</div>

---

## Bugs

-   无法分辨带入库是函数还是类，所以全当作类名处理了
-   无法解析出导入包的方法
-   无法高亮内联的for循环产生的变量名
-   同一名字多次定义时，会产生错误的高亮
-   无法多层嵌套的调用，只能高亮第一层，例如`a.b`或者`a.b()`
-   无法确定变量的作用域，所有变量都全局高亮
