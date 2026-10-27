"""Tests for terminal URL handling without opening a browser."""
import re
import unittest
from unittest.mock import Mock, patch

from chiterm import Gtk, Vte
from gi.repository import Gdk
from terminal_links import MATCH_FLAGS, URL_PATTERN, _on_pressed, normalize_url


class TerminalLinkTests(unittest.TestCase):
    def test_vte_accepts_the_match_expression(self):
        self.assertIsNotNone(Vte.Regex.new_for_match(URL_PATTERN, -1, MATCH_FLAGS))
        self.assertEqual(re.search(URL_PATTERN, 'see HTTPS://example.com').group(),
                         'HTTPS://example.com')

    def test_plain_text_trims_prose_punctuation_but_keeps_balanced_parentheses(self):
        self.assertEqual(normalize_url('https://example.com/wiki/Name_(topic)).', from_text=True),
                         'https://example.com/wiki/Name_(topic)')
        self.assertEqual(normalize_url('HTTPS://example.com/path.)', from_text=True),
                         'HTTPS://example.com/path')
        self.assertEqual(normalize_url('https://example.com/path?', from_text=False),
                         'https://example.com/path?')

    def test_rejects_non_web_and_invalid_urls(self):
        for value in ('file:///etc/passwd', 'javascript:alert(1)', 'https://',
                      'https://example.com:bad/', 'https://example.com/\nother'):
            with self.subTest(value=value):
                self.assertIsNone(normalize_url(value))

    def test_control_click_opens_explicit_hyperlink(self):
        gesture = Mock()
        gesture.get_current_event_state.return_value = Gdk.ModifierType.CONTROL_MASK
        terminal = Mock()
        gesture.get_widget.return_value = terminal
        terminal.check_hyperlink_at.return_value = 'https://example.com/a?'
        with patch('terminal_links.Gio.AppInfo.launch_default_for_uri') as launch:
            _on_pressed(gesture, 1, 12, 24)
        launch.assert_called_once_with('https://example.com/a?', None)
        gesture.set_state.assert_called_once_with(Gtk.EventSequenceState.CLAIMED)
        terminal.check_match_at.assert_not_called()

    def test_control_click_opens_plain_text_match(self):
        gesture = Mock()
        gesture.get_current_event_state.return_value = Gdk.ModifierType.CONTROL_MASK
        terminal = Mock()
        gesture.get_widget.return_value = terminal
        terminal.check_hyperlink_at.return_value = None
        terminal.check_match_at.return_value = ('https://example.com/a).', 1)
        with patch('terminal_links.Gio.AppInfo.launch_default_for_uri') as launch:
            _on_pressed(gesture, 1, 12, 24)
        launch.assert_called_once_with('https://example.com/a', None)

    def test_unmodified_click_and_unsupported_hyperlink_pass_through(self):
        gesture = Mock()
        terminal = Mock()
        gesture.get_widget.return_value = terminal
        gesture.get_current_event_state.return_value = Gdk.ModifierType(0)
        with patch('terminal_links.Gio.AppInfo.launch_default_for_uri') as launch:
            _on_pressed(gesture, 1, 0, 0)
            terminal.check_hyperlink_at.assert_not_called()
            gesture.get_current_event_state.return_value = Gdk.ModifierType.CONTROL_MASK
            terminal.check_hyperlink_at.return_value = 'file:///etc/passwd'
            _on_pressed(gesture, 1, 0, 0)
            launch.assert_not_called()
        gesture.set_state.assert_not_called()
        terminal.check_match_at.assert_not_called()


if __name__ == '__main__':
    unittest.main()
