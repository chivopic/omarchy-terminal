# Contributing / 参与贡献

## English

Bug reports and small pull requests are welcome. For a bug report, include your Linux distribution, GTK/VTE versions, steps to reproduce, expected behavior, and what happened instead. Remove private paths, tokens, and terminal output before sharing logs.

For a change, create a branch, keep the pull request focused, and explain how you verified it. Run `/usr/bin/python -m py_compile chiterm.py` and exercise affected behavior in a graphical session. Add a regression test when it would help prevent the issue from returning.

Keep the English and Chinese README files consistent when changing user-facing behavior.

## 中文

欢迎提交 bug 报告和范围清晰的 PR。报告问题时，请提供 Linux 发行版、GTK/VTE 版本、复现步骤、预期行为和实际结果。分享日志前，请删除私人路径、令牌和终端中的敏感内容。

修改时请创建分支，让每个 PR 聚焦一个问题，并说明验证方式。运行 `/usr/bin/python -m py_compile chiterm.py`，并在图形会话中验证受影响的功能；适合时请补充回归测试。

修改面向用户的行为时，请同步更新中英文 README。
