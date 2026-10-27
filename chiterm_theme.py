"""Read Omarchy's active palette without modifying desktop configuration."""
from pathlib import Path
import tomllib

import gi
gi.require_version('Gdk', '4.0')
from gi.repository import Gdk

PALETTE_KEYS = (
    'background', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'foreground',
    'muted', 'bright_red', 'bright_green', 'bright_yellow', 'bright_blue',
    'bright_magenta', 'bright_cyan', 'bright_foreground',
)


def theme_path():
    return Path.home() / '.local/state/omarchy/current/theme/colors.toml'


def read_theme(path):
    """Return validated RGBA values, or None for a missing/invalid palette."""
    try:
        with path.open('rb') as file:
            colors = tomllib.load(file)
        parsed = {}
        for name in PALETTE_KEYS:
            value = colors[name]
            color = Gdk.RGBA()
            if not isinstance(value, str) or not color.parse(value):
                return None
            parsed[name] = color
        return parsed['foreground'], parsed['background'], [parsed[name] for name in PALETTE_KEYS]
    except (OSError, KeyError, tomllib.TOMLDecodeError):
        return None
