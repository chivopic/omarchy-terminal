"""GTK integration tests for pane and tab focus behavior."""
import os
import time
import unittest

from chiterm import Application, GLib, Gtk, TerminalWindow, Vte


def pump_until(predicate, timeout=3):
    context = GLib.MainContext.default()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        while context.iteration(False):
            pass
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError('Timed out waiting for GTK or the shell')


class TerminalWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_shell = os.environ.get('SHELL')
        os.environ['SHELL'] = '/bin/sh'
        cls.app = Application()
        cls.app.register(None)

    @classmethod
    def tearDownClass(cls):
        if cls.original_shell is None:
            os.environ.pop('SHELL', None)
        else:
            os.environ['SHELL'] = cls.original_shell

    def setUp(self):
        self.win = TerminalWindow(self.app)
        self.win.present()
        pump_until(lambda: self.win.active_terminal.get_pty() is not None)

    def tearDown(self):
        self.win.destroy()
        while GLib.MainContext.default().iteration(False):
            pass

    def split(self):
        self.win.split(Gtk.Orientation.HORIZONTAL)
        terminal = self.win.active_terminal
        pump_until(lambda: terminal.get_pty() is not None)
        return terminal

    def exit_shell(self, terminal):
        terminal.feed_child(b'exit\n')
        pump_until(lambda: self.win.page_for(terminal) is None)

    def test_switching_tabs_restores_last_focused_pane(self):
        self.split()
        focused = self.win.active_terminal
        self.win.new_tab()
        self.win.change_tab(-1)
        self.assertIs(self.win.active_terminal, focused)

    def test_background_pane_exit_does_not_redirect_new_split(self):
        background = self.win.active_terminal
        self.split()
        self.win.new_tab()
        foreground = self.win.active_terminal
        pump_until(lambda: foreground.get_pty() is not None)
        self.exit_shell(background)
        self.assertIs(self.win.active_terminal, foreground)
        self.win.split(Gtk.Orientation.VERTICAL)
        self.assertIsInstance(foreground.get_parent(), Gtk.Paned)
        self.assertEqual(self.win.notebook.get_current_page(), 1)

    def test_unfocused_pane_exit_keeps_current_focus(self):
        first = self.win.active_terminal
        second = self.split()
        third = self.split()
        self.exit_shell(first)
        self.assertIs(self.win.active_terminal, third)
        self.assertIsNot(self.win.active_terminal, second)

    def test_background_focused_pane_exit_restores_remaining_pane(self):
        remaining = self.win.active_terminal
        exiting = self.split()
        self.win.new_tab()
        self.exit_shell(exiting)
        self.win.change_tab(-1)
        self.assertIs(self.win.active_terminal, remaining)

    def test_background_tab_exit_keeps_selected_tab_and_pane(self):
        background = self.win.active_terminal
        self.win.new_tab()
        foreground = self.win.active_terminal
        self.exit_shell(background)
        self.assertEqual(self.win.notebook.get_n_pages(), 1)
        self.assertIs(self.win.active_terminal, foreground)

    def test_closing_selected_pane_focuses_its_sibling(self):
        remaining = self.win.active_terminal
        self.split()
        self.win.close_active()
        self.assertIs(self.win.active_terminal, remaining)
        self.assertEqual(self.win.notebook.get_n_pages(), 1)

    def test_inactive_pane_title_does_not_replace_active_pane_title(self):
        first = self.win.active_terminal
        second = self.split()
        second.feed(b'\x1b]0;active pane\x07')
        page = self.win.page_for(second)
        label = self.win.notebook.get_tab_label(page)
        pump_until(lambda: label.get_text() == 'active pane')
        first.feed(b'\x1b]0;inactive pane\x07')
        pump_until(lambda: first.get_window_title() == 'inactive pane')
        self.assertEqual(label.get_text(), 'active pane')

    def test_search_is_case_insensitive_and_treats_punctuation_as_text(self):
        terminal = self.win.active_terminal
        terminal.feed(b'\r\nBuild v1.2 [ready]\r\n')
        pump_until(lambda: terminal.get_cursor_position().row >= 1)
        self.win.open_search()
        self.win.search_entry.set_text('V1.2 [READY]')
        pump_until(self.win.find_text)
        self.assertEqual(terminal.get_text_selected(Vte.Format.TEXT), 'v1.2 [ready]')
        self.win.search_entry.set_text('v1x2')
        self.assertFalse(self.win.find_text())
        self.assertEqual(self.win.search_status.get_text(), 'No matches')

    def test_search_targets_only_the_focused_pane(self):
        first = self.win.active_terminal
        first.feed(b'\r\nneedle in first pane\r\n')
        pump_until(lambda: first.get_cursor_position().row >= 1)
        second = self.split()
        self.win.search_entry.set_text('needle in first pane')
        self.assertFalse(self.win.find_text())
        self.assertIs(self.win.active_terminal, second)

    def test_search_advances_and_wraps_between_matches(self):
        terminal = self.win.active_terminal
        terminal.feed(b'\r\napple\r\nAPPLE\r\n')
        self.win.search_entry.set_text('apple')
        pump_until(self.win.find_text)
        first = terminal.get_text_selected(Vte.Format.TEXT)
        self.assertTrue(self.win.find_text())
        second = terminal.get_text_selected(Vte.Format.TEXT)
        self.assertNotEqual(first, second)
        self.assertTrue(self.win.find_text())
        self.assertEqual(first, terminal.get_text_selected(Vte.Format.TEXT))

    def test_keyboard_pane_cycle_respects_nested_splits_and_tabs(self):
        first = self.win.active_terminal
        second = self.split()
        third = self.split()
        self.win.change_pane(1)
        self.assertIs(self.win.active_terminal, first)
        self.win.change_pane(1)
        self.assertIs(self.win.active_terminal, second)
        self.win.change_pane(-1)
        self.assertIs(self.win.active_terminal, first)
        self.win.change_pane(-1)
        self.assertIs(self.win.active_terminal, third)
        self.win.new_tab()
        isolated = self.win.active_terminal
        self.win.change_pane(1)
        self.assertIs(self.win.active_terminal, isolated)

    def test_zoom_restores_nested_panes_without_restarting_shells(self):
        first = self.win.active_terminal
        second = self.split()
        third = self.split()
        page = self.win.page_for(third)
        self.win.toggle_pane_zoom()
        self.assertTrue(third.get_visible())
        self.assertFalse(first.get_visible())
        self.assertFalse(second.get_visible())
        self.assertIsNotNone(first.get_pty())
        self.assertIsNotNone(second.get_pty())
        self.win.toggle_pane_zoom()
        self.assertTrue(first.get_visible())
        self.assertTrue(second.get_visible())
        self.assertNotIn(page, self.win.maximized_by_page)
        self.assertIs(self.win.active_terminal, third)

    def test_zoom_is_per_tab_and_navigation_restores_layout(self):
        first = self.win.active_terminal
        second = self.split()
        self.win.toggle_pane_zoom()
        self.win.new_tab()
        self.win.change_tab(-1)
        self.assertFalse(first.get_visible())
        self.assertIs(self.win.active_terminal, second)
        self.win.change_pane(1)
        self.assertTrue(first.get_visible())
        self.assertIs(self.win.active_terminal, first)

    def test_zoom_restores_before_hidden_pane_exits_or_new_split(self):
        hidden = self.win.active_terminal
        active = self.split()
        self.win.toggle_pane_zoom()
        self.exit_shell(hidden)
        self.assertIs(self.win.active_terminal, active)
        self.win.split(Gtk.Orientation.VERTICAL)
        self.assertTrue(active.get_visible())
        self.assertTrue(self.win.active_terminal.get_visible())


if __name__ == '__main__':
    unittest.main()
