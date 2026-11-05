#!/usr/bin/env python3
"""Install, update, or uninstall Chiterm in a user-selected prefix."""
import argparse
import os
from pathlib import Path
import shutil
import sys


RUNTIME_FILES = (
    'chiterm.py',
    'command_model.py',
    'command_palette.py',
    'config.py',
    'diagnostics.py',
    'terminal_links.py',
    'terminal_search.py',
    'themes.py',
    'version.py',
)


def install_paths(prefix=None, destdir=None):
    prefix = Path(prefix if prefix is not None else Path.home() / '.local').expanduser()
    prefix = Path(os.path.abspath(prefix))
    destdir = destdir or None
    if destdir is None:
        return prefix, prefix
    staging_root = Path(destdir).expanduser()
    staging_root = Path(os.path.abspath(staging_root))
    return prefix, staging_root / prefix.relative_to(prefix.anchor)


def desktop_exec_quote(argument):
    """Quote one executable path according to Desktop Entry Exec rules."""
    if any(ord(character) < 32 or ord(character) == 127 for character in argument):
        raise ValueError('Desktop application paths cannot contain control characters')
    unsupported = set("\\\"'$`%<>|&;*?#()~")
    if any(character in unsupported for character in argument):
        raise ValueError('Installation paths used by desktop entries may contain spaces, '
                         'but not quotes, backslashes, shell metacharacters, or percent signs')
    return f'"{argument}"'


def launcher_contents():
    return '''#!/usr/bin/python3
from pathlib import Path
import runpy
import sys

app_dir = Path(__file__).resolve().parent.parent / "lib" / "chiterm"
sys.path.insert(0, str(app_dir))
runpy.run_path(str(app_dir / "chiterm.py"), run_name="__main__")
'''


def desktop_contents(prefix):
    launcher = prefix / 'bin' / 'chiterm'
    quoted_launcher = desktop_exec_quote(str(launcher))
    return (
        '[Desktop Entry]\n'
        'Type=Application\n'
        'Name=Chiterm\n'
        'Comment=Native GTK terminal for Linux\n'
        f'Exec={quoted_launcher}\n'
        f'TryExec={launcher}\n'
        'Icon=utilities-terminal\n'
        'Terminal=false\n'
        'Categories=System;TerminalEmulator;\n'
    )


def install(prefix=None, destdir=None, source_root=None):
    logical_prefix, root = install_paths(prefix, destdir)
    source_root = Path(source_root) if source_root is not None else Path(__file__).resolve().parent
    app_dir = root / 'lib' / 'chiterm'
    bin_dir = root / 'bin'
    desktop_dir = root / 'share' / 'applications'
    desktop_entry = desktop_contents(logical_prefix)
    app_dir.mkdir(parents=True, exist_ok=True)
    bin_dir.mkdir(parents=True, exist_ok=True)
    desktop_dir.mkdir(parents=True, exist_ok=True)

    for filename in RUNTIME_FILES:
        shutil.copyfile(source_root / filename, app_dir / filename)
    launcher = bin_dir / 'chiterm'
    launcher.write_text(launcher_contents(), encoding='utf-8')
    launcher.chmod(0o755)
    (desktop_dir / 'chiterm.desktop').write_text(desktop_entry, encoding='utf-8')
    return root


def uninstall(prefix=None, destdir=None):
    _logical_prefix, root = install_paths(prefix, destdir)
    owned_files = [root / 'lib' / 'chiterm' / filename for filename in RUNTIME_FILES]
    owned_files.extend((
        root / 'bin' / 'chiterm',
        root / 'share' / 'applications' / 'chiterm.desktop',
    ))
    removed = []
    for path in owned_files:
        try:
            path.unlink()
        except FileNotFoundError:
            continue
        removed.append(path)
    try:
        (root / 'lib' / 'chiterm').rmdir()
    except OSError:
        pass
    return removed


def main(arguments=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', default=str(Path.home() / '.local'),
                        help='installation prefix (default: ~/.local)')
    parser.add_argument('--destdir', default=os.environ.get('DESTDIR') or None,
                        help='stage files beneath this directory for packaging')
    parser.add_argument('--uninstall', action='store_true', help='remove Chiterm files from the prefix')
    options = parser.parse_args(arguments)
    try:
        if options.uninstall:
            removed = uninstall(options.prefix, options.destdir)
            print(f'Removed {len(removed)} Chiterm files.')
        else:
            root = install(options.prefix, options.destdir)
            print(f'Installed Chiterm under {root}.')
    except (OSError, ValueError) as error:
        print(f'Chiterm installer: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
