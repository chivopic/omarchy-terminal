#!/usr/bin/env python3
"""Chiterm: a native terminal powered by GTK 4 and VTE."""
import os
import sys
import weakref
from pathlib import Path
from urllib.parse import unquote, urlparse

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Vte', '3.91')
from gi.repository import Gio, GLib, Gtk, Pango, Vte
from terminal_links import install_link_handler

APP_ID = 'io.github.chivopic.Chiterm'
# PCRE2 compile flags required by VTE: UTF, Unicode, multiline and caseless.
SEARCH_FLAGS = 0x00080000 | 0x00020000 | 0x00000400 | 0x00000008


def current_directory(terminal):
    """Use VTE's OSC 7 directory when it identifies a local directory."""
    uri = terminal.get_current_directory_uri() if terminal else None
    if uri:
        parsed = urlparse(uri)
        if parsed.scheme == 'file' and parsed.netloc in ('', 'localhost', GLib.get_host_name()):
            path = unquote(parsed.path)
            if os.path.isdir(path):
                return path
    return str(Path.home())


class TerminalWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title='Chiterm')
        self.set_default_size(1000, 650)
        self.active_terminal = None
        self.focused_by_page = {}
        self.search_terminal = None
        self.search_query = None
        self.font_scale = 1.0
        self.set_icon_name('utilities-terminal')

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(container)
        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label='Chiterm'))
        add = Gtk.Button.new_from_icon_name('tab-new-symbolic')
        add.set_tooltip_text('New tab (Ctrl+Shift+T)')
        add.connect('clicked', lambda *_: self.new_tab())
        header.pack_start(add)
        menu = Gio.Menu()
        for label, action in [('New Tab', 'new-tab'), ('Split Left / Right', 'split-right'),
                              ('Split Top / Bottom', 'split-down'), ('Close Pane', 'close-pane'),
                              ('Next Pane', 'next-pane'), ('Previous Pane', 'previous-pane'),
                              ('Copy', 'copy'), ('Paste', 'paste'), ('Find', 'find'), ('Zoom In', 'zoom-in'),
                              ('Zoom Out', 'zoom-out'), ('Reset Zoom', 'zoom-reset')]:
            menu.append(label, 'win.' + action)
        menu_button = Gtk.MenuButton(icon_name='open-menu-symbolic', menu_model=menu)
        header.pack_end(menu_button)
        container.append(header)
        self.search_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.search_bar.set_margin_top(6)
        self.search_bar.set_margin_bottom(6)
        self.search_bar.set_margin_start(8)
        self.search_bar.set_margin_end(8)
        self.search_entry = Gtk.SearchEntry(hexpand=True, placeholder_text='Find in current pane')
        self.search_entry.connect('changed', lambda *_: self.find_text())
        self.search_entry.connect('activate', lambda *_: self.find_text())
        self.search_bar.append(self.search_entry)
        self.search_status = Gtk.Label(label='')
        self.search_bar.append(self.search_status)
        for icon, tooltip, callback in [
            ('go-up-symbolic', 'Previous match', lambda: self.find_text(previous=True)),
            ('go-down-symbolic', 'Next match', self.find_text),
            ('window-close-symbolic', 'Close search', self.close_search),
        ]:
            button = Gtk.Button.new_from_icon_name(icon)
            button.set_tooltip_text(tooltip)
            button.connect('clicked', lambda _button, cb=callback: cb())
            self.search_bar.append(button)
        self.search_bar.set_visible(False)
        container.append(self.search_bar)
        self.notebook = Gtk.Notebook(scrollable=True, hexpand=True, vexpand=True)
        self.notebook.connect('switch-page', self.on_switch_page)
        container.append(self.notebook)
        for name, callback in {
            'new-tab': self.new_tab, 'split-right': lambda: self.split(Gtk.Orientation.HORIZONTAL),
            'split-down': lambda: self.split(Gtk.Orientation.VERTICAL), 'close-pane': self.close_active,
            'copy': self.copy, 'paste': self.paste, 'zoom-in': lambda: self.zoom(0.1),
            'find': self.open_search, 'find-next': self.find_text,
            'find-previous': lambda: self.find_text(previous=True),
            'next-pane': lambda: self.change_pane(1),
            'previous-pane': lambda: self.change_pane(-1),
            'zoom-out': lambda: self.zoom(-0.1), 'zoom-reset': lambda: self.zoom(None),
            'next-tab': lambda: self.change_tab(1), 'previous-tab': lambda: self.change_tab(-1),
        }.items():
            action = Gio.SimpleAction.new(name, None)
            action.connect('activate', lambda _action, _param, cb=callback: cb())
            self.add_action(action)
        self.new_tab()

    def make_terminal(self, cwd):
        terminal = Vte.Terminal(hexpand=True, vexpand=True)
        terminal.set_scrollback_lines(10000)
        terminal.set_font(Pango.FontDescription.from_string('monospace 11'))
        terminal.set_font_scale(self.font_scale)
        terminal.set_mouse_autohide(True)
        install_link_handler(terminal)
        terminal.connect('child-exited', lambda term, _status: self.remove_terminal(term))
        terminal.connect('window-title-changed', self.update_title)
        focus = Gtk.EventControllerFocus()
        focus.connect('enter', lambda controller: self.set_active(controller.get_widget()))
        terminal.add_controller(focus)
        shell = os.environ.get('SHELL') or '/bin/sh'
        if not os.path.isfile(shell) or not os.access(shell, os.X_OK):
            shell = '/bin/sh'
        terminal.spawn_async(Vte.PtyFlags.DEFAULT, cwd, [shell], None,
                             GLib.SpawnFlags.DEFAULT, None, None, -1, None, self.spawned, None)
        return terminal

    def spawned(self, terminal, pid, error, _data):
        if error:
            terminal.feed(('\r\nCould not start shell: ' + str(error) + '\r\n').encode())

    def set_active(self, terminal):
        changed = self.active_terminal is not terminal
        page = self.page_for(terminal)
        if page is not None:
            self.focused_by_page[page] = terminal
        self.active_terminal = terminal
        self.update_title(terminal)
        if changed and self.search_bar.get_visible():
            self.find_text()

    def update_title(self, terminal):
        page = self.page_for(terminal)
        if page and self.focused_by_page.get(page) == terminal:
            label = self.notebook.get_tab_label(page)
            if label:
                label.set_text((terminal.get_window_title() or 'Terminal')[:30])

    def page_for(self, widget):
        for index in range(self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(index)
            if widget == page or widget.is_ancestor(page):
                return page
        return None

    def new_tab(self):
        cwd = current_directory(self.active_terminal)
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        terminal = self.make_terminal(cwd)
        page.append(terminal)
        index = self.notebook.append_page(page, Gtk.Label(label='Terminal'))
        self.notebook.set_tab_reorderable(page, True)
        self.notebook.set_current_page(index)
        self.set_active(terminal)
        terminal.grab_focus()

    def split(self, orientation):
        old = self.active_terminal
        if not old or not self.page_for(old):
            return
        parent = old.get_parent()
        new = self.make_terminal(current_directory(old))
        if isinstance(parent, Gtk.Paned):
            start = parent.get_start_child() == old
            if start:
                parent.set_start_child(None)
            else:
                parent.set_end_child(None)
        else:
            parent.remove(old)
        paned = Gtk.Paned(orientation=orientation, hexpand=True, vexpand=True, wide_handle=True)
        paned.set_start_child(old)
        paned.set_end_child(new)
        paned.set_resize_start_child(True)
        paned.set_resize_end_child(True)
        if isinstance(parent, Gtk.Paned):
            (parent.set_start_child if start else parent.set_end_child)(paned)
        else:
            parent.append(paned)
        self.set_active(new)
        new.grab_focus()

    def remove_terminal(self, terminal):
        page = self.page_for(terminal)
        if page is None:
            return
        selected_page = self.notebook.get_nth_page(self.notebook.get_current_page())
        was_active = terminal == self.active_terminal
        parent = terminal.get_parent()
        if isinstance(parent, Gtk.Paned):
            sibling = parent.get_end_child() if parent.get_start_child() == terminal else parent.get_start_child()
            grandparent = parent.get_parent()
            is_start = isinstance(grandparent, Gtk.Paned) and grandparent.get_start_child() == parent
            parent.set_start_child(None)
            parent.set_end_child(None)
            if isinstance(grandparent, Gtk.Paned):
                setter = grandparent.set_start_child if is_start else grandparent.set_end_child
                setter(None)
                setter(sibling)
            else:
                grandparent.remove(parent)
                grandparent.append(sibling)
            if self.focused_by_page.get(page) == terminal:
                self.focused_by_page[page] = self.first_terminal(sibling)
            if page == selected_page and was_active:
                self.focus_page(page)
        else:
            index = self.notebook.page_num(page)
            self.focused_by_page.pop(page, None)
            self.notebook.remove_page(index)
            if self.notebook.get_n_pages() == 0:
                self.active_terminal = None
                self.close()
            elif page == selected_page:
                self.focus_current_page()

    def first_terminal(self, widget):
        if isinstance(widget, Vte.Terminal):
            return widget
        elif isinstance(widget, Gtk.Paned):
            return self.first_terminal(widget.get_start_child())
        elif isinstance(widget, Gtk.Box):
            return self.first_terminal(widget.get_first_child())
        return None

    def focus_page(self, page):
        terminal = self.focused_by_page.get(page) or self.first_terminal(page)
        if terminal:
            self.set_active(terminal)
            terminal.grab_focus()

    def focus_current_page(self):
        page = self.notebook.get_nth_page(self.notebook.get_current_page())
        if page:
            self.focus_page(page)

    def on_switch_page(self, _notebook, page, _index):
        self.focus_page(page)

    def close_active(self):
        if self.active_terminal:
            self.remove_terminal(self.active_terminal)

    def copy(self):
        if self.active_terminal:
            self.active_terminal.copy_clipboard_format(Vte.Format.TEXT)

    def paste(self):
        if self.active_terminal:
            self.active_terminal.paste_clipboard()

    def open_search(self):
        self.search_bar.set_visible(True)
        if self.search_entry.get_text():
            self.find_text()
        self.search_entry.grab_focus()

    def close_search(self):
        self.search_bar.set_visible(False)
        self.clear_search()
        self.search_status.set_text('')
        if self.active_terminal:
            self.active_terminal.grab_focus()

    def clear_search(self):
        terminal = self.search_terminal() if self.search_terminal else None
        if terminal is not None:
            terminal.search_set_regex(None, 0)
        self.search_terminal = None
        self.search_query = None

    def find_text(self, previous=False):
        terminal = self.active_terminal
        query = self.search_entry.get_text()
        if not terminal or not query:
            self.clear_search()
            self.search_status.set_text('')
            return False
        searched = self.search_terminal() if self.search_terminal else None
        if searched is not terminal or self.search_query != query:
            self.clear_search()
            # Escape user input so that search is literal, including punctuation.
            pattern = GLib.regex_escape_string(query, -1)
            regex = Vte.Regex.new_for_search(pattern, -1, SEARCH_FLAGS)
            terminal.search_set_regex(regex, 0)
            terminal.search_set_wrap_around(True)
            self.search_terminal, self.search_query = weakref.ref(terminal), query
        found = terminal.search_find_previous() if previous else terminal.search_find_next()
        self.search_status.set_text('' if found else 'No matches')
        return found

    def zoom(self, delta):
        self.font_scale = 1.0 if delta is None else max(0.5, min(2.0, self.font_scale + delta))
        def visit(widget):
            if isinstance(widget, Vte.Terminal):
                widget.set_font_scale(self.font_scale)
            child = widget.get_first_child()
            while child:
                visit(child)
                child = child.get_next_sibling()
        visit(self.notebook)

    def change_tab(self, step):
        count = self.notebook.get_n_pages()
        if count:
            self.notebook.set_current_page((self.notebook.get_current_page() + step) % count)

    def change_pane(self, step):
        page = self.notebook.get_nth_page(self.notebook.get_current_page())
        if not page:
            return
        def terminals(widget):
            if isinstance(widget, Vte.Terminal):
                return [widget]
            if isinstance(widget, Gtk.Paned):
                return terminals(widget.get_start_child()) + terminals(widget.get_end_child())
            if isinstance(widget, Gtk.Box):
                return terminals(widget.get_first_child())
            return []
        panes = terminals(page)
        if self.active_terminal in panes:
            terminal = panes[(panes.index(self.active_terminal) + step) % len(panes)]
            self.set_active(terminal)
            terminal.grab_focus()


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.NON_UNIQUE)

    def do_activate(self):
        win = TerminalWindow(self)
        win.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        for action, keys in {
            'new-tab': ['<Control><Shift>t'], 'close-pane': ['<Control><Shift>w'],
            'split-right': ['<Control><Shift>d'], 'split-down': ['<Control><Shift>e'],
            'copy': ['<Control><Shift>c'], 'paste': ['<Control><Shift>v'],
            'find': ['<Control><Shift>f'], 'find-next': ['<Control><Shift>g'],
            'find-previous': ['<Control><Shift><Alt>g'],
            'next-pane': ['<Control><Shift>bracketright'],
            'previous-pane': ['<Control><Shift>bracketleft'],
            'next-tab': ['<Control>Page_Down'], 'previous-tab': ['<Control>Page_Up'],
            'zoom-in': ['<Control>plus', '<Control>equal'], 'zoom-out': ['<Control>minus'],
            'zoom-reset': ['<Control>0'],
        }.items():
            self.set_accels_for_action('win.' + action, keys)


if __name__ == '__main__':
    sys.exit(Application().run(sys.argv))
