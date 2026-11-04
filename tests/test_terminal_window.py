"""GTK integration tests for pane and tab focus behavior."""
import os
import tempfile
import time
import unittest
import weakref
from unittest.mock import patch

from chiterm import Application, Gdk, GLib, Gtk, TerminalWindow, Vte
from config import ConfigStore
from themes import THEMES


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
        if (os.environ.get('SKIP_GUI_TESTS') == '1'
                and os.environ.get('REQUIRE_GUI_TESTS') != '1'):
            raise unittest.SkipTest('GUI tests skipped by SKIP_GUI_TESTS; run make test-gui')
        display_available = Gtk.init_check() and Gdk.Display.get_default() is not None
        if not display_available:
            message = 'GTK display unavailable; GUI tests need Xvfb or a desktop session'
            if os.environ.get('REQUIRE_GUI_TESTS') == '1':
                raise RuntimeError(message)
            raise unittest.SkipTest(message)
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
        self.config_tmp = tempfile.TemporaryDirectory()
        self.config_store = ConfigStore(os.path.join(self.config_tmp.name, 'config.json'))
        self.win = TerminalWindow(self.app, config_store=self.config_store)
        self.win.present()
        pump_until(lambda: self.win.active_terminal.get_pty() is not None)

    def tearDown(self):
        self.win.destroy()
        while GLib.MainContext.default().iteration(False):
            pass
        self.config_tmp.cleanup()

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
        with patch.object(self.win, 'confirm_close', side_effect=lambda _message, done: done(True)):
            self.win.close_active()
        self.assertIs(self.win.active_terminal, remaining)
        self.assertEqual(self.win.notebook.get_n_pages(), 1)

    def test_cancelled_close_keeps_pane_and_shell(self):
        terminal = self.split()
        with patch.object(self.win, 'confirm_close', side_effect=lambda _message, done: done(False)):
            self.win.close_active()
        self.assertIs(self.win.active_terminal, terminal)
        self.assertIsNotNone(self.win.page_for(terminal))
        self.assertIsNotNone(terminal.get_pty())

    def test_confirmed_close_targets_original_pane(self):
        first = self.win.active_terminal
        second = self.split()
        with patch.object(self.win, 'confirm_close') as confirm:
            self.win.close_active()
            self.win.set_active(first)
            confirm.call_args.args[1](True)
        self.assertIsNone(self.win.page_for(second))
        self.assertIs(self.win.active_terminal, first)

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

    def test_ignore_case_search_treats_punctuation_as_text(self):
        terminal = self.win.active_terminal
        terminal.feed(b'\r\nBuild v1.2 [ready]\r\n')
        pump_until(lambda: terminal.get_cursor_position().row >= 1)
        self.win.open_search()
        self.win.case_mode.set_selected(2)
        self.win.search_entry.set_text('V1.2 [READY]')
        pump_until(lambda: terminal.get_text_selected(Vte.Format.TEXT) == 'v1.2 [ready]')
        self.assertEqual(terminal.get_text_selected(Vte.Format.TEXT), 'v1.2 [ready]')
        self.win.search_entry.set_text('v1x2')
        self.assertFalse(self.win.find_text())
        self.assertEqual(self.win.search_status.get_text(), 'No matches')

    def test_smart_case_and_case_sensitive_search_modes(self):
        terminal = self.win.active_terminal
        terminal.feed(b'\r\napple APPLE\r\n')
        pump_until(lambda: terminal.get_cursor_position().row >= 1)
        self.win.search_entry.set_text('APPLE')
        pump_until(lambda: terminal.get_text_selected(Vte.Format.TEXT) == 'APPLE')
        self.assertEqual(terminal.get_text_selected(Vte.Format.TEXT), 'APPLE')
        self.win.case_mode.set_selected(1)
        self.win.search_entry.set_text('apple')
        pump_until(lambda: terminal.get_text_selected(Vte.Format.TEXT) == 'apple')
        self.assertEqual(terminal.get_text_selected(Vte.Format.TEXT), 'apple')

    def test_regex_search_and_invalid_pattern_status(self):
        terminal = self.win.active_terminal
        terminal.feed(b'\r\nitem 42; item 7\r\n')
        pump_until(lambda: terminal.get_cursor_position().row >= 1)
        self.win.regex_toggle.set_active(True)
        self.win.search_entry.set_text(r'item \d+')
        pump_until(lambda: terminal.get_text_selected(Vte.Format.TEXT) == 'item 42')
        self.assertEqual(terminal.get_text_selected(Vte.Format.TEXT), 'item 42')
        self.win.search_entry.set_text('(')
        self.assertFalse(self.win.find_text())
        self.assertEqual(self.win.search_status.get_text(), 'Invalid regular expression')

    def test_theme_changes_all_panes_without_restarting_shells(self):
        first = self.win.active_terminal
        second = self.split()
        first_pty, second_pty = first.get_pty(), second.get_pty()
        first_process, second_process = (os.tcgetpgrp(first_pty.get_fd()),
                                         os.tcgetpgrp(second_pty.get_fd()))
        self.win.toggle_pane_zoom()
        self.assertFalse(first.get_visible())
        self.win.new_tab()
        background_tab_terminal = self.win.active_terminal
        pump_until(lambda: background_tab_terminal.get_pty() is not None)
        background_process = os.tcgetpgrp(background_tab_terminal.get_pty().get_fd())

        self.win.lookup_action('theme').activate(GLib.Variant.new_string('paper-bloom'))

        self.assertEqual(self.win.theme_action.get_state().get_string(), 'paper-bloom')
        self.assertEqual(os.tcgetpgrp(first.get_pty().get_fd()), first_process)
        self.assertEqual(os.tcgetpgrp(second.get_pty().get_fd()), second_process)
        self.assertEqual(os.tcgetpgrp(background_tab_terminal.get_pty().get_fd()), background_process)
        expected = self.win.rgba(THEMES['paper-bloom'].background)
        for terminal in (first, second, background_tab_terminal):
            color = terminal.get_color_background_for_draw()
            self.assertAlmostEqual(color.red, expected.red, places=3)
            self.assertAlmostEqual(color.green, expected.green, places=3)
            self.assertAlmostEqual(color.blue, expected.blue, places=3)

    def test_new_pane_inherits_and_persists_selected_theme(self):
        self.win.lookup_action('theme').activate(GLib.Variant.new_string('harbor-dusk'))
        new_window = TerminalWindow(self.app, config_store=self.config_store)
        try:
            self.assertEqual(new_window.current_theme, 'harbor-dusk')
            self.assertEqual(self.config_store.load_theme(), 'harbor-dusk')
        finally:
            new_window.destroy()

        self.win.split(Gtk.Orientation.HORIZONTAL)
        terminal = self.win.active_terminal
        pump_until(lambda: terminal.get_pty() is not None)
        expected = self.win.rgba(THEMES['harbor-dusk'].background)
        color = terminal.get_color_background_for_draw()
        self.assertAlmostEqual(color.red, expected.red, places=3)
        self.assertAlmostEqual(color.green, expected.green, places=3)
        self.assertAlmostEqual(color.blue, expected.blue, places=3)

    def test_theme_save_failure_is_visible_and_keeps_session_theme(self):
        with patch.object(self.config_store, 'save_theme', side_effect=OSError('read only')):
            self.win.set_theme('sage-ledger')
        self.assertEqual(self.win.current_theme, 'sage-ledger')
        self.assertTrue(self.win.status_revealer.get_reveal_child())
        self.assertIn('could not be saved', self.win.status_label.get_text())

    def test_search_keyboard_escape_and_shift_enter(self):
        terminal = self.win.active_terminal
        terminal.feed(b'\r\nalpha\r\nbeta\r\n')
        pump_until(lambda: terminal.get_cursor_position().row >= 2)
        self.win.regex_toggle.set_active(True)
        self.win.search_entry.set_text('alpha|beta')
        pump_until(lambda: terminal.get_text_selected(Vte.Format.TEXT) in ('alpha', 'beta'))
        first = terminal.get_text_selected(Vte.Format.TEXT)
        self.assertIn(first, ('alpha', 'beta'))
        self.assertTrue(self.win.on_search_key_pressed(
            None, Gdk.KEY_Return, 0, Gdk.ModifierType.SHIFT_MASK))
        self.assertNotEqual(terminal.get_text_selected(Vte.Format.TEXT), first)
        self.assertTrue(self.win.on_search_key_pressed(None, Gdk.KEY_Escape, 0, 0))
        self.assertFalse(self.win.search_bar.get_visible())
        self.assertIsNone(terminal.search_get_regex())

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
        pump_until(lambda: terminal.get_cursor_position().row >= 2)
        self.win.search_entry.set_text('apple')
        pump_until(lambda: terminal.get_text_selected(Vte.Format.TEXT) != '')
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

    def test_search_status_and_selection_follow_focused_pane(self):
        first = self.win.active_terminal
        first.feed(b'\r\nunique-needle\r\n')
        pump_until(lambda: first.get_cursor_position().row >= 1)
        second = self.split()
        self.win.open_search()
        self.win.search_entry.set_text('unique-needle')
        self.assertFalse(self.win.find_text())
        self.assertEqual(self.win.search_status.get_text(), 'No matches')
        self.win.change_pane(-1)
        self.assertIs(self.win.active_terminal, first)
        self.assertEqual(self.win.search_status.get_text(), '')
        self.assertEqual(first.get_text_selected(Vte.Format.TEXT), 'unique-needle')
        self.assertIsNone(second.search_get_regex())

    def test_empty_and_closed_search_clear_vte_regex(self):
        terminal = self.win.active_terminal
        self.win.open_search()
        self.win.search_entry.set_text('needle')
        self.assertIsNotNone(terminal.search_get_regex())
        self.win.search_entry.set_text('')
        self.assertIsNone(terminal.search_get_regex())
        self.win.search_entry.set_text('needle')
        self.win.close_search()
        self.assertIsNone(terminal.search_get_regex())
        self.assertIsNone(self.win.search_terminal)
        self.win.open_search()
        self.assertIsNotNone(terminal.search_get_regex())

    def test_search_cache_does_not_own_terminal(self):
        terminal = self.win.active_terminal
        self.win.search_entry.set_text('needle')
        self.assertIsInstance(self.win.search_terminal, weakref.ReferenceType)
        self.assertIs(self.win.search_terminal(), terminal)


    def tracked_new_tab(self):
        spawned_pids = []
        original = self.win.spawned

        def spawned(terminal, pid, error, data):
            if not error:
                spawned_pids.append(pid)
            original(terminal, pid, error, data)

        self.win.spawned = spawned
        try:
            self.win.new_tab()
            pump_until(lambda: bool(spawned_pids))
        finally:
            self.win.spawned = original
        return self.win.active_terminal, spawned_pids[0]

    def test_closing_tab_terminates_idle_shell(self):
        terminal, pid = self.tracked_new_tab()
        terminal_ref = weakref.ref(terminal)
        with patch.object(self.win, 'confirm_close', lambda _message, done: done(True)):
            self.win.close_active()
        del terminal
        pump_until(lambda: terminal_ref() is None and not os.path.exists(f'/proc/{pid}'))

    def test_closing_tab_terminates_foreground_process(self):
        terminal, shell_pid = self.tracked_new_tab()
        terminal.feed_child(b'sleep 60\n')
        pump_until(lambda: os.tcgetpgrp(terminal.get_pty().get_fd()) > 0
                   and os.tcgetpgrp(terminal.get_pty().get_fd()) != shell_pid)
        foreground_pid = os.tcgetpgrp(terminal.get_pty().get_fd())
        with patch.object(self.win, 'confirm_close', lambda _message, done: done(True)):
            self.win.close_active()
        del terminal
        pump_until(lambda: not os.path.exists(f'/proc/{shell_pid}')
                   and not os.path.exists(f'/proc/{foreground_pid}'))


if __name__ == '__main__':
    unittest.main()
