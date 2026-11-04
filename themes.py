"""Built-in Chiterm terminal palettes (custom designs, not vendor themes)."""
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class Theme:
    name: str
    foreground: str
    background: str
    cursor: str
    selection_foreground: str
    selection_background: str
    ansi: tuple[str, ...]


DEFAULT_THEME = 'midnight-fern'

# ANSI order: black, red, green, yellow, blue, magenta, cyan, white,
# followed by the corresponding bright colors.
THEMES = MappingProxyType({
    'midnight-fern': Theme(
        name='Midnight Fern', foreground='#dce8dd', background='#111a18',
        cursor='#a6e3a1', selection_foreground='#101813', selection_background='#9ccf94',
        ansi=(
            '#5d6f66', '#f07178', '#a6e3a1', '#e5c890', '#82aaff', '#c792ea', '#89ddff', '#dce8dd',
            '#586b62', '#ff8b92', '#b5f3aa', '#f1d69a', '#9db9ff', '#d7a9f5', '#a7e6ff', '#f1f7f1',
        ),
    ),
    'harbor-dusk': Theme(
        name='Harbor Dusk', foreground='#d9e6f2', background='#111a26',
        cursor='#8bd5ca', selection_foreground='#101824', selection_background='#91b6d4',
        ansi=(
            '#5a6b80', '#f27d85', '#8bd5a8', '#e9c879', '#83aaff', '#c6a0f6', '#78dce8', '#d9e6f2',
            '#596b82', '#ff9299', '#9ce6b8', '#f4d58a', '#9bbcff', '#d4b3fa', '#91e9f2', '#f1f6fc',
        ),
    ),
    'paper-bloom': Theme(
        name='Paper Bloom', foreground='#352a25', background='#fbf3e8',
        cursor='#9b4137', selection_foreground='#fffaf3', selection_background='#76564a',
        ansi=(
            '#473832', '#a63d40', '#3f6d4a', '#8a5b13', '#345f91', '#855282', '#287078', '#978778',
            '#76665a', '#b54b4d', '#507f58', '#9b6c20', '#4771a2', '#956393', '#3c8288', '#8b7a6c',
        ),
    ),
    'sage-ledger': Theme(
        name='Sage Ledger', foreground='#24352d', background='#f0f5eb',
        cursor='#426b58', selection_foreground='#1d2c25', selection_background='#bdcbb7',
        ansi=(
            '#34463d', '#a13f42', '#386a4b', '#795c16', '#3d6090', '#79577a', '#276e72', '#829084',
            '#68796e', '#b34d4e', '#4c7f5c', '#8c6d27', '#4d73a1', '#8b688d', '#3a7f82', '#78887c',
        ),
    ),
})
