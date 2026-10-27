# Omarchy Terminal

[English](README.md) | 简体中文

一个受 iTerm2 日常工作流启发的原生终端，面向 Omarchy 和其他 Linux 桌面。应用基于 GTK 4 和 VTE，每个面板都运行真实 shell，支持终端程序、颜色和滚动回看。

## MVP 功能

- 标签页：支持拖动排序和 shell 提供的标题
- 左右、上下分屏，支持嵌套
- 复制、粘贴、滚动回看和字体缩放
- 当 shell 通过 OSC 7 报告当前目录时，新标签和分屏会继承聚焦面板的目录；否则从主目录启动
- 原生 GTK 窗口，支持 Wayland 和 X11

这是早期 MVP，目前没有配置档、搜索、会话恢复、自动同步 Omarchy 主题或关闭运行中 shell 的确认提示。

## 运行

在 Omarchy / Arch Linux 上，如果缺少依赖，请先安装：

```sh
sudo pacman -S python python-gobject gtk4 vte4
```

克隆仓库并启动应用：

```sh
git clone https://github.com/chivopic/omarchy-terminal.git
cd omarchy-terminal
/usr/bin/python omarchy_terminal.py
```

请使用系统 Python：上面的软件包为它提供 GTK 和 VTE 绑定。应用优先使用 `$SHELL` 指向的可执行文件，不可用时回退到 `/bin/sh`。GTK 界面跟随桌面设置；终端颜色目前使用 VTE 默认值。

## 快捷键

| 快捷键 | 操作 |
| --- | --- |
| Ctrl+Shift+T | 新建标签 |
| Ctrl+Shift+D | 左右分屏 |
| Ctrl+Shift+E | 上下分屏 |
| Ctrl+Shift+W | 关闭当前面板（或标签） |
| Ctrl+Shift+C / V | 复制 / 粘贴 |
| Ctrl+Page Up / Down | 上一个 / 下一个标签 |
| Ctrl++ / Ctrl+- / Ctrl+0 | 放大 / 缩小 / 重置字体 |

关闭面板或窗口会结束其中的 shell 和前台进程，请先保存工作。点击面板可切换焦点，标题栏菜单也提供主要操作。

## 许可证

MIT
