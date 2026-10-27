# Roadmap / 路线图

[English](#english) · [简体中文](#简体中文)

## English

This is a proposed order of work, not a release schedule. Priorities may change with feedback; items are planned unless a status is shown.

### 1. Make the basics dependable

- **Pane focus:** preserve the focused pane when switching tabs and when another shell exits. A fix and regression tests are under review in [#1](https://github.com/chivopic/omarchy-terminal/pull/1).
- **Safer closing:** confirm before closing panes or windows with potentially active work, with a clear way to cancel.
- **Repeatable checks:** run GTK/VTE regression tests in CI and cover shell startup, pane lifecycle, and keyboard shortcuts.

### 2. Improve everyday navigation

- Search terminal scrollback with next/previous match controls.
- Move between panes from the keyboard and make the focused pane easier to identify.
- Offer a simple way to configure font size, scrollback, and common shortcuts.

### 3. Fit into Omarchy

- Read the active Omarchy terminal colors and update the application when the theme changes, with a usable fallback outside Omarchy.
- Provide an installable desktop entry and an easy update/uninstall path for Omarchy and Arch Linux.

### 4. Restore workspaces

- Restore tab and split layouts on request, with clear behavior for working directories that are no longer available.
- Explore profiles for shell, font, and colors once the core settings are stable.

Session restoration would recreate shells and layouts; it would not resume previously running processes. The exact scope and order will be refined as the application matures.

## 简体中文

以下是建议的开发顺序，不是发布时间表。优先级会根据反馈调整；除已标注状态的项目外，均为计划事项。

### 1. 让基础功能更可靠

- **面板焦点：**切换标签或其他 shell 退出时保留正确的焦点。修复和回归测试正在 [#1](https://github.com/chivopic/omarchy-terminal/pull/1) 中审阅。
- **安全关闭：**关闭可能仍有工作的面板或窗口前提示确认，并允许取消。
- **可重复验证：**在 CI 中运行 GTK/VTE 回归测试，覆盖 shell 启动、面板生命周期和快捷键。

### 2. 改善日常操作

- 在终端滚动回看中搜索，并跳转到上一个或下一个结果。
- 支持键盘切换面板，让当前焦点更容易辨认。
- 提供简单的字体大小、滚动回看和常用快捷键设置。

### 3. 融入 Omarchy

- 读取当前 Omarchy 终端配色并在主题变化时更新，同时为其他桌面提供可用的默认配色。
- 提供可安装的桌面入口，以及适合 Omarchy 和 Arch Linux 的更新、卸载方式。

### 4. 恢复工作区

- 按需恢复标签和分屏布局，并明确处理已不存在的工作目录。
- 基础设置稳定后，探索 shell、字体和配色的配置档。

会话恢复将重新创建 shell 和布局，不会恢复之前运行的进程。具体范围和顺序会随着项目发展调整。
