# Chiterm roadmap / 路线图

[English](#english) · [简体中文](#简体中文)

## English

This is a proposed order of work, not a release schedule. Priorities may change with feedback.

### Available in this branch

- Nested splits, remembered pane focus, keyboard pane navigation, and close confirmation.
- Literal, case-insensitive search in the focused pane and Omarchy palette synchronization.
- GTK/VTE integration tests for pane lifecycle, search, confirmation, and themes.

### Next: dependable daily use

- Run GTK/VTE tests in CI and test keyboard shortcuts and real Wayland interaction.
- Improve search navigation, including multiple matches on one line and optional regular expressions.
- Add preferences for font, scrollback, shortcuts, and colors.
- Package a desktop entry with documented installation, updates, and removal.

### Later: deeper terminal workflows

- Restore tab and split layouts on request, handling unavailable directories clearly.
- Explore profiles and shell integration for prompt navigation and richer context.
- Evaluate additional iTerm2-inspired features such as paste history and keyboard selection.

Restoration would recreate shells and layouts; it would not resume previously running processes.

## 简体中文

以下是建议的开发顺序，不是发布时间表。优先级会根据反馈调整。

### 当前分支已实现

- 嵌套分屏、焦点记忆、键盘切换面板和关闭确认。
- 在当前面板进行不区分大小写的纯文本搜索，以及同步 Omarchy 配色。
- 覆盖面板生命周期、搜索、关闭确认和主题的 GTK/VTE 集成测试。

### 下一步：可靠的日常使用

- 在 CI 中运行 GTK/VTE 测试，并验证快捷键和真实 Wayland 交互。
- 改善搜索跳转，包括同一行中的多个匹配项和可选正则表达式。
- 增加字体、滚动回看、快捷键和配色设置。
- 提供桌面入口，并说明安装、更新和卸载方法。

### 后续：更深入的终端工作流

- 按需恢复标签和分屏布局，明确处理不可用的目录。
- 探索配置档和 shell 集成，以支持提示符导航及更丰富的上下文。
- 评估粘贴历史和键盘选择等 iTerm2 风格功能。

会话恢复将重新创建 shell 和布局，不会恢复之前运行的进程。
