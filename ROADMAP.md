# Roadmap / 路线图

[English](#english) · [简体中文](#简体中文)

## English

Chiterm is an early preview. This roadmap describes direction, not release dates.

### Shipped

- Tabs, nested splits, pane focus, and temporary pane zoom
- Shell working-directory reuse through OSC 7
- Scrollback search, pane navigation, and Ctrl-click HTTP(S) links
- Four built-in terminal color palettes
- GTK/VTE regression suite and Xvfb CI configuration

### Next

- Synchronize terminal colors with Omarchy while keeping sensible defaults on other desktops
- Add a desktop entry and a simple install/update path
- Explore configurable profiles and optional workspace restoration

Workspace restoration would recreate shells and layouts; it would not resume running processes. Priorities may change with feedback.

## 简体中文

Chiterm 仍处于早期预览阶段。路线图描述方向，不代表发布时间。

### 已完成

- 标签页、嵌套分屏、面板焦点和临时最大化面板
- 通过 OSC 7 沿用 shell 工作目录
- 滚动回看搜索、键盘切换面板和 Ctrl 单击 HTTP(S) 链接
- 四种内置终端配色
- GTK/VTE 回归测试与 Xvfb CI 配置

### 后续方向

- 同步 Omarchy 终端配色，同时为其他桌面保留合理默认值
- 提供桌面入口和简单的安装、更新方式
- 探索可配置的配置档和可选的工作区恢复

工作区恢复会重新创建 shell 和布局，不会恢复仍在运行的进程。优先级可能根据反馈调整。
