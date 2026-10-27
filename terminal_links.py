"""Open HTTP(S) links in a terminal with Control-click."""

import sys
from urllib.parse import urlsplit

from gi.repository import Gdk, Gio, GLib, Gtk, Vte

# VTE requires PCRE2 UTF and multiline modes. Stop at whitespace, control
# characters and common quoting delimiters; trailing punctuation is trimmed
# separately so URLs in prose remain useful.
MATCH_FLAGS = 0x00080000 | 0x00000400
URL_PATTERN = r"(?i)https?://[^\s\x00-\x1f\x7f<>\"']+"


def normalize_url(value, *, from_text=False):
    """Return a safe browser URL, or None for invalid/unsupported targets."""
    if not value or any(ord(char) < 32 or ord(char) == 127 for char in value):
        return None
    if from_text:
        # Preserve balanced parentheses (common in wiki URLs), stripping only
        # unmatched closing delimiters added by surrounding prose.
        while value:
            trimmed = value.rstrip('.,;:!?')
            for opening, closing in [('(', ')'), ('[', ']'), ('{', '}')]:
                while trimmed.endswith(closing) and trimmed.count(closing) > trimmed.count(opening):
                    trimmed = trimmed[:-1]
            if trimmed == value:
                break
            value = trimmed
    try:
        parts = urlsplit(value)
        if parts.scheme.lower() not in ('http', 'https') or not parts.hostname:
            return None
        # Accessing port also validates bracketed hosts and malformed ports.
        parts.port
    except ValueError:
        return None
    return value


def install_link_handler(terminal):
    """Enable explicit OSC 8 links and register a Control-click handler."""
    terminal.set_allow_hyperlink(True)
    regex = Vte.Regex.new_for_match(URL_PATTERN, -1, MATCH_FLAGS)
    tag = terminal.match_add_regex(regex, 0)
    terminal.match_set_cursor_name(tag, 'pointer')
    click = Gtk.GestureClick.new()
    click.set_button(1)
    click.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
    click.connect('pressed', _on_pressed)
    terminal.add_controller(click)


def _on_pressed(gesture, _press_count, x, y):
    if not (gesture.get_current_event_state() & Gdk.ModifierType.CONTROL_MASK):
        return
    terminal = gesture.get_widget()
    target = terminal.check_hyperlink_at(x, y)
    # Explicit hyperlink targets are authoritative, even if unsupported.
    from_text = target is None
    if from_text:
        target, _tag = terminal.check_match_at(x, y)
    target = normalize_url(target, from_text=from_text)
    if target is None:
        return
    gesture.set_state(Gtk.EventSequenceState.CLAIMED)
    try:
        Gio.AppInfo.launch_default_for_uri(target, None)
    except GLib.Error as error:
        # Failure to launch the desktop handler must not crash the terminal.
        print(f'Could not open link: {error}', file=sys.stderr)
