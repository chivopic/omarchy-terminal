"""GTK command palette popover backed by the pure command model."""
import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')
from gi.repository import Gdk, GLib, Gtk, Pango

from command_model import filter_commands


class CommandPalette(Gtk.Popover):
    def __init__(self, anchor, on_activate, on_closed):
        super().__init__()
        self.set_parent(anchor)
        self.set_autohide(True)
        self.set_has_arrow(False)
        self.set_position(Gtk.PositionType.BOTTOM)
        self.set_size_request(520, 420)
        self.on_activate = on_activate
        self.on_closed = on_closed
        self.commands = []
        self.visible_commands = []
        self.rows = []
        self.pending_command = None

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(10)
        content.set_margin_end(10)
        self.search_entry = Gtk.SearchEntry(placeholder_text='Search commands, themes, and tabs')
        # ``search-changed`` is deliberately debounced by GTK. Use ``changed``
        # so Enter can never execute a row from the previous query.
        self.search_entry.connect('changed', self.on_query_changed)
        self.search_entry.connect('activate', lambda *_: self.activate_selected())
        keys = Gtk.EventControllerKey()
        keys.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        keys.connect('key-pressed', self.on_key_pressed)
        self.search_entry.add_controller(keys)
        content.append(self.search_entry)

        self.no_results = Gtk.Label(label='No matching commands', xalign=0)
        content.append(self.no_results)
        self.scroller = Gtk.ScrolledWindow(min_content_height=330, min_content_width=500,
                                           hscrollbar_policy=Gtk.PolicyType.NEVER)
        self.list_box = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        self.list_box.connect('row-activated', self.on_row_activated)
        self.scroller.set_child(self.list_box)
        content.append(self.scroller)
        self.set_child(content)
        self.connect('closed', self.on_popover_closed)

    def open(self, commands):
        self.pending_command = None
        self.commands = list(commands)
        self.search_entry.set_text('')
        self.refresh_rows()
        self.popup()
        self.search_entry.grab_focus()

    def on_query_changed(self, *_args):
        self.refresh_rows()

    def refresh_rows(self):
        row = self.list_box.get_first_child()
        while row:
            following = row.get_next_sibling()
            self.list_box.remove(row)
            row = following
        self.rows = []
        self.visible_commands = filter_commands(self.commands, self.search_entry.get_text())
        self.no_results.set_visible(not self.visible_commands)
        self.scroller.set_visible(bool(self.visible_commands))
        for command in self.visible_commands:
            row = Gtk.ListBoxRow()
            line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            line.set_margin_top(5)
            line.set_margin_bottom(5)
            line.set_margin_start(7)
            line.set_margin_end(7)
            title = Gtk.Label(label=command.label, xalign=0, hexpand=True)
            title.set_ellipsize(Pango.EllipsizeMode.END)
            title.set_max_width_chars(48)
            title.set_tooltip_text(command.label)
            line.append(title)
            shortcut = Gtk.Label(label=command.shortcut, xalign=1)
            if command.shortcut:
                shortcut.set_tooltip_text(f'Keyboard shortcut: {command.shortcut}')
            line.append(shortcut)
            row.set_child(line)
            self.list_box.append(row)
            self.rows.append(row)
        if self.rows:
            self.list_box.select_row(self.rows[0])
            self.scroll_row_into_view(self.rows[0])

    def on_key_pressed(self, _controller, keyval, _keycode, _state):
        if keyval == Gdk.KEY_Escape:
            self.pending_command = None
            self.popdown()
            return True
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self.activate_selected()
            return True
        if keyval in (Gdk.KEY_Up, Gdk.KEY_Down):
            self.move_selection(-1 if keyval == Gdk.KEY_Up else 1)
            return True
        return False

    def move_selection(self, direction):
        if not self.rows:
            return
        selected = self.list_box.get_selected_row()
        index = selected.get_index() if selected else 0
        index = (index + direction) % len(self.rows)
        self.list_box.select_row(self.rows[index])
        self.scroll_row_into_view(self.rows[index])

    def scroll_row_into_view(self, row):
        def scroll():
            adjustment = self.scroller.get_vadjustment()
            if adjustment.get_upper() > adjustment.get_page_size():
                fraction = row.get_index() / max(1, len(self.rows) - 1)
                adjustment.set_value(fraction * (adjustment.get_upper() - adjustment.get_page_size()))
            return GLib.SOURCE_REMOVE
        GLib.idle_add(scroll)

    def on_row_activated(self, _list_box, row):
        index = row.get_index()
        if 0 <= index < len(self.visible_commands):
            self.choose(self.visible_commands[index])

    def activate_selected(self):
        row = self.list_box.get_selected_row()
        if row is None and self.rows:
            row = self.rows[0]
        if row is not None:
            self.on_row_activated(self.list_box, row)

    def choose(self, command):
        self.pending_command = command
        self.popdown()

    def on_popover_closed(self, *_args):
        command, self.pending_command = self.pending_command, None
        # Let GTK finish moving focus out of the popover, then restore the
        # original pane before a command changes focus itself.
        def finish_close():
            self.on_closed()
            if command is not None:
                self.on_activate(command)
            return GLib.SOURCE_REMOVE
        GLib.idle_add(finish_close)
