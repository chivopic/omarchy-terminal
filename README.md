# Omarchy Terminal

A small, native terminal inspired by the everyday workflow of iTerm2, built for Omarchy and other Linux desktops. It uses GTK 4 and VTE, so each pane runs a real shell with terminal applications, colors and scrollback.

## MVP

- Tabs, with drag-to-reorder and shell-provided titles
- Horizontal and vertical splits, including nested splits
- Copy, paste, scrollback and font zoom
- New tabs and splits start in the focused pane's directory when the shell reports it via OSC 7; otherwise they start in your home directory
- Native GTK window, usable on Wayland and X11

This is an early MVP, not a complete iTerm2 replacement. It does not yet include profiles, search, session restoration, automatic Omarchy theme synchronization, or a confirmation when closing a running shell.

## Run

On Omarchy / Arch Linux, install the system dependencies if needed:

```sh
sudo pacman -S python python-gobject gtk4 vte4
```

Then run:

```sh
/usr/bin/python omarchy_terminal.py
```

The application uses `$SHELL`, falling back to `/bin/sh`. The GTK theme follows your desktop settings; terminal colors currently use VTE defaults.

## Shortcuts

| Shortcut | Action |
| --- | --- |
| Ctrl+Shift+T | New tab |
| Ctrl+Shift+D | Split left/right |
| Ctrl+Shift+E | Split top/bottom |
| Ctrl+Shift+W | Close focused pane (or tab) |
| Ctrl+Shift+C / V | Copy / paste |
| Ctrl+Page Up / Down | Previous / next tab |
| Ctrl++ / Ctrl+- / Ctrl+0 | Zoom in / out / reset |

Closing a pane or window ends its shell and any foreground process; save your work first. Click a pane to focus it. The menu in the header exposes the same main actions.

## Tests

With the dependencies above and a running graphical session, run:

```sh
/usr/bin/python -m unittest discover -s tests -v
```

These GTK integration tests launch `/bin/sh` in real VTE panes and exercise tab focus, shell exits, nested splits, and titles. They need a GTK display; they can also run with GTK's Broadway backend on a headless machine.

## License

MIT
