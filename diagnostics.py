"""Small dependency and display diagnostics that work before GTK imports."""
import sys

from version import VERSION


def check_environment(output=None):
    output = sys.stdout if output is None else output
    print(f'Chiterm {VERSION}', file=output)
    print(f'Python: {sys.version.split()[0]}', file=output)

    try:
        import gi
    except Exception as error:
        print(f'GTK: unavailable ({error})', file=output)
        print('VTE: unavailable (Python GObject bindings are missing)', file=output)
        print('Display: not checked', file=output)
        print('Install python-gobject, gtk4 and vte4 (Omarchy/Arch), or '
              'python3-gi, gir1.2-gtk-4.0 and gir1.2-vte-3.91 (Ubuntu).', file=output)
        return 1

    gtk = None
    gdk = None
    vte = None
    try:
        gi.require_version('Gtk', '4.0')
        gi.require_version('Gdk', '4.0')
        from gi.repository import Gdk, Gtk
        gtk, gdk = Gtk, Gdk
        print(f'GTK: {Gtk.get_major_version()}.{Gtk.get_minor_version()}.'
              f'{Gtk.get_micro_version()}', file=output)
    except Exception as error:
        print(f'GTK: unavailable ({error})', file=output)

    try:
        gi.require_version('Vte', '3.91')
        from gi.repository import Vte
        vte = Vte
        print(f'VTE: {Vte.get_major_version()}.{Vte.get_minor_version()}.'
              f'{Vte.get_micro_version()}', file=output)
    except Exception as error:
        print(f'VTE: unavailable ({error})', file=output)

    display_available = False
    if gtk is not None and gdk is not None:
        try:
            display_available = bool(Gtk.init_check() and Gdk.Display.get_default())
        except Exception as error:
            print(f'Display: check failed ({error})', file=output)
        else:
            print(f'Display: {"available" if display_available else "not available"}', file=output)
    else:
        print('Display: not checked (GTK is unavailable)', file=output)

    if gtk is None or vte is None:
        print('Install GTK 4 and VTE 3.91 bindings for your distribution.', file=output)
        return 1
    if not display_available:
        print('Start Chiterm from a Wayland or X11 desktop session.', file=output)
        return 1
    return 0


def handle_cli(arguments, output=None):
    """Handle diagnostic-only flags; return None for normal application startup."""
    output = sys.stdout if output is None else output
    if '--version' in arguments:
        print(VERSION, file=output)
        return 0
    if '--check' in arguments:
        return check_environment(output)
    return None
