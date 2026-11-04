# Chiterm user guide

[简体中文](USER_GUIDE.zh-CN.md) · [Back to README](../README.md)

## Tabs and panes

Use the **+** button or **New Tab** in the header menu to open a tab. Click a pane to focus it. Split the focused pane left/right or top/bottom from the menu or with the shortcuts below. Drag a divider to resize panes and drag tab labels to reorder tabs.

New tabs and splits use the focused pane's local working directory when the shell reports it with OSC 7. Otherwise, they start in your home directory. Remote directory reports are not used as local paths.

Pane zoom hides the other panes in that tab until you toggle it again or move focus to another pane. Hidden shells keep running.

## Search

Press **Ctrl+Shift+F** to search the focused pane's scrollback. Search wraps around the scrollback and updates as you type. Use the controls in the search bar to choose:

- **Smart Case:** lowercase queries ignore case; any uppercase letter makes the search case-sensitive.
- **Case Sensitive** or **Ignore Case:** force a case mode.
- **Regular expression:** treat the query as a PCRE2 expression. Invalid expressions show an error in the bar.

The search bar reports `No matches` when a query has no result. Search applies to the focused pane only.

## Links and clipboard

Ctrl-click an HTTP(S) link to open it in your default browser. Ordinary clicks remain available to terminal applications. Copy and paste use the desktop clipboard.

## Shortcuts

| Shortcut | Action |
| --- | --- |
| Ctrl+Shift+T | New tab |
| Ctrl+Shift+D | Split left/right |
| Ctrl+Shift+E | Split top/bottom |
| Ctrl+Shift+W | Close focused pane or tab |
| Ctrl+Shift+C / V | Copy / paste |
| Ctrl+Shift+F | Find in the focused pane |
| Ctrl+Shift+G / Ctrl+Shift+Alt+G | Next / previous match |
| Enter / Shift+Enter in search | Next / previous match |
| F3 / Shift+F3 in search | Next / previous match |
| Escape in search | Close search |
| Ctrl+Shift+] / Ctrl+Shift+[ | Next / previous pane |
| Ctrl+Shift+Enter | Zoom / restore focused pane |
| Ctrl+Page Down / Page Up | Next / previous tab |
| Ctrl++ or Ctrl+= / Ctrl+- / Ctrl+0 | Increase / decrease / reset font size |

## Limits and troubleshooting

Closing a pane or window asks for confirmation. Confirming stops the affected shell and its foreground process. Chiterm does not restore tabs or panes after exit. Profiles and automatic Omarchy color synchronization are not available.

- **`No module named gi` or a missing GTK/VTE namespace:** install the system packages and run `/usr/bin/python`, not a virtual environment without those bindings.
- **The window does not open:** start Chiterm from a Wayland or X11 desktop session and check the launching terminal for errors.
- **A new pane starts in your home directory:** configure the shell to report its local directory with OSC 7.
