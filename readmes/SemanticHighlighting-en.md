# Known Bugs in Highlighting

This document lists known bugs in the highlighting feature of the code editor. If you encounter any issues, please check this list first to see if they are already known.

And these bugs are not critical, if you corrctly write your code and format it, you can avoid most of them. So for its hard to fix, I will not fix them in the short term. Unless I found its a totally mess.

<div align="center">English | <a href="./SemanticHighlighting-zh-CN.md">中文</a></div>

---

## Bugs

-   Cannot distinguish whether an imported library is a function or a class, so they are all treated as class names
-   Cannot parse methods from imported packages
-   Cannot highlight variable names produced by inline for loops
-   When the same name is defined multiple times, incorrect highlighting occurs
-   Cannot handle multi-level nested calls, can only highlight the first level, such as `a.b` or `a.b()`
-   Cannot determine the scope of variables, all variables are highlighted globally
