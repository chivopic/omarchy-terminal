# Contributing / 参与贡献

## English

Bug reports and focused pull requests are welcome. GitHub provides short forms for [bug reports](https://github.com/chivopic/omarchy-terminal/issues/new?template=bug_report.yml) and [feature requests](https://github.com/chivopic/omarchy-terminal/issues/new?template=feature_request.yml).

For a pull request, describe the problem and change, keep the scope focused, and include the checks you ran. Add a regression test for behavior that could break again. Update both READMEs when a change affects the main project description; update the [user guide](docs/USER_GUIDE.md) and its [Chinese version](docs/USER_GUIDE.zh-CN.md) when usage changes.

### Checks

- `make check` runs syntax checks and automatically discovers display-free search, theme, config, link, installer, and diagnostics tests. It uses the system Python with GTK/VTE bindings; install the packages listed in the README first. The GUI class is explicitly skipped by this target.
- Search pattern logic alone can be tested with `python3 -m unittest discover -s tests -p 'test_terminal_search.py'` and needs only Python.
- `make test-gui` runs the real GTK/VTE integration suite, including search, theme switching, persistence, and pane lifecycle, and fails if no display is available.
- On a headless machine, run `xvfb-run -a dbus-run-session -- make test-all`.
- `python3 install.py --prefix "/tmp/chiterm test"` exercises installation without changing the default user prefix. Installer tests use temporary directories and verify uninstall leaves settings and unrelated files intact.

Ordinary `unittest discover` skips the GUI test class when there is no display. A skipped GUI suite is not evidence that interface behavior passed. GitHub Actions runs all checks under Xvfb.

Please remove private paths, tokens, and sensitive terminal output from issues and logs. See the [user guide](docs/USER_GUIDE.md) for current behavior and the [roadmap](ROADMAP.md) for planned work.

## 简体中文

欢迎提交 bug 报告和范围清晰的 PR。GitHub 提供简短表单：[报告问题](https://github.com/chivopic/omarchy-terminal/issues/new?template=bug_report.yml)和[功能建议](https://github.com/chivopic/omarchy-terminal/issues/new?template=feature_request.yml)。

提交 PR 时，请说明问题和改动，控制范围，并列出运行过的检查。容易回归的行为应补充测试。修改项目简介时请同步更新中英文 README；修改使用方式时，请同步更新[中文使用手册](docs/USER_GUIDE.zh-CN.md)和[英文手册](docs/USER_GUIDE.md)。

### 检查

- `make check` 会运行语法检查，并自动发现无需图形显示的搜索、主题、配置、链接、安装器和诊断测试。它使用带 GTK/VTE 绑定的系统 Python，请先按 README 安装依赖。该目标会显式跳过 GUI 测试类。
- 只测试搜索模式可运行 `python3 -m unittest discover -s tests -p 'test_terminal_search.py'`，只需要 Python。
- `make test-gui` 会运行真实 GTK/VTE 集成测试，覆盖搜索、主题切换、配置持久化和面板生命周期；没有显示服务时会失败。
- 无头环境可运行 `xvfb-run -a dbus-run-session -- make test-all`。
- `python3 install.py --prefix "/tmp/chiterm test"` 可在临时前缀中试装，不会更改默认用户目录。安装测试使用临时目录，并确认卸载保留配置和无关文件。

普通的 `unittest discover` 在没有显示服务时会跳过 GUI 测试类。跳过 GUI 测试并不表示界面行为已经通过验证。GitHub Actions 会在 Xvfb 下运行所有检查。

提交 issue 或日志前，请删除私人路径、令牌和敏感的终端输出。当前行为见[中文使用手册](docs/USER_GUIDE.zh-CN.md)，计划见[路线图](ROADMAP.md)。
