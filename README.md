# Chiterm

English | [简体中文](README.zh-CN.md)

A small, native terminal inspired by the everyday workflow of iTerm2, built for Omarchy and other Linux desktops. It uses GTK 4 and VTE, so each pane runs a real shell with terminal applications, colors and scrollback.

![Illustration of a tabbed terminal with two split panes](assets/terminal-preview.svg)

*Workspace illustration; the actual appearance depends on your desktop theme.*

## MVP

- Tabs, with drag-to-reorder and shell-provided titles
- Horizontal and vertical splits, including nested splits
- Copy, paste, scrollback, literal search and font zoom
- Keyboard pane navigation and a focused-pane indicator
- Close confirmation and automatic Omarchy terminal palette updates
- New tabs and splits start in the focused pane's directory when the shell reports it via OSC 7; otherwise they start in your home directory
- Native GTK window, usable on Wayland and X11

This is an early MVP, not a complete iTerm2 replacement. See [Current limitations](#current-limitations) before using it for important work.

## Run

Chiterm needs Python 3.11+, GTK 4.10+ and VTE’s GTK 4 bindings. On Omarchy / Arch Linux, install the system dependencies if needed:

```sh
sudo pacman -S python python-gobject gtk4 vte4
```

Clone the repository and start the application:

```sh
git clone https://github.com/chivopic/omarchy-terminal.git
cd omarchy-terminal
/usr/bin/python chiterm.py
```

Use the system Python because the packages above provide its GTK and VTE bindings. The application uses `$SHELL` when it points to an executable file, falling back to `/bin/sh` otherwise. The GTK theme follows your desktop settings. Chiterm reads the active Omarchy colors and checks for changes every two seconds. Outside Omarchy, or when no complete palette is available at startup, VTE defaults are used.

## Working directories

New tabs and splits use the focused terminal’s reported local directory. Your shell must emit OSC 7 for this to work; without a valid local directory report, they start in your home directory. Remote directory reports are not used as local paths.

## Working with panes and tabs

Use the **+** button or the header menu to open a tab. Click a pane to focus it, then use the menu or shortcuts below to split it. Drag the divider to resize panes; drag a tab label to reorder tabs. Closing the last pane in a tab closes that tab.

## Current limitations

- Closing a pane or window always asks for confirmation; it does not detect whether a command is running.
- Tabs and panes are not restored after the application exits.
- Profiles and session restoration are not implemented. Search is literal and case-insensitive; VTE search may not step through multiple matches on the same line.

## Troubleshooting

- **`No module named gi`**: install `python-gobject` and launch with `/usr/bin/python`, not a virtual environment without system bindings.
- **GTK or VTE namespace unavailable**: check that `gtk4` and `vte4` are installed.
- **No window opens**: start the application from a running Wayland or X11 desktop session and read any error printed in the launching terminal.
- **A new pane opens in your home directory**: check whether your shell reports its directory through OSC 7.

## Roadmap

Next up: stronger terminal integration, settings, packaging, and workspace restoration. See the [roadmap](ROADMAP.md#english) for priorities and current status.

## Contributing

Bug reports and focused pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Shortcuts

| Shortcut | Action |
| --- | --- |
| Ctrl+Shift+T | New tab |
| Ctrl+Shift+D | Split left/right |
| Ctrl+Shift+E | Split top/bottom |
| Ctrl+Shift+W | Close focused pane (or tab) |
| Ctrl+Shift+Left / Right | Previous / next pane |
| Ctrl+Shift+F | Find in focused pane |
| Ctrl+Shift+G | Find next |
| Ctrl+Shift+Alt+G | Find previous |
| Ctrl+Shift+C | Copy selection |
| Ctrl+Shift+V | Paste |
| Ctrl+Page Up | Previous tab |
| Ctrl+Page Down | Next tab |
| Ctrl++ or Ctrl+= | Zoom in |
| Ctrl+- | Zoom out |
| Ctrl+0 | Reset zoom |

Closing a pane or window may terminate its shell and foreground process; save your work first. Click a pane to focus it. The menu in the header exposes the same main actions.

## Tests

With the dependencies above and a running graphical session, run:

```sh
/usr/bin/python -m unittest discover -s tests -v
```

These GTK integration tests launch `/bin/sh` in real VTE panes and exercise tab focus, shell exits, nested splits, search, confirmation, and themes. They need a GTK display; they can also run with GTK's Broadway backend on a headless machine.

## License

MIT
