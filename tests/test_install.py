"""Temporary-prefix install/update/uninstall tests; never touch a user install."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import gi
gi.require_version('GioUnix', '2.0')
from gi.repository import GioUnix, GLib

from install import RUNTIME_FILES, desktop_contents, desktop_exec_quote, install, uninstall
from version import VERSION


REPOSITORY = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def test_install_with_spaces_runs_outside_the_source_tree(self):
        prefix = self.directory / 'home with spaces' / '.local'
        install(prefix, source_root=REPOSITORY)
        app_dir = prefix / 'lib' / 'chiterm'
        for filename in RUNTIME_FILES:
            self.assertEqual((app_dir / filename).read_bytes(),
                             (REPOSITORY / filename).read_bytes())

        launcher = prefix / 'bin' / 'chiterm'
        self.assertTrue(launcher.stat().st_mode & 0o111)
        result = subprocess.run([str(launcher), '--version'], cwd=self.directory,
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), VERSION)
        desktop_file = prefix / 'share' / 'applications' / 'chiterm.desktop'
        entry = desktop_file.read_text()
        self.assertIn(f'Exec="{launcher}"', entry)
        self.assertIn(f'TryExec={launcher}', entry)
        key_file = GLib.KeyFile()
        key_file.load_from_file(str(desktop_file), GLib.KeyFileFlags.NONE)
        self.assertEqual(key_file.get_string('Desktop Entry', 'Exec'), f'"{launcher}"')
        self.assertEqual(key_file.get_string('Desktop Entry', 'TryExec'), str(launcher))
        self.assertIsNotNone(GioUnix.DesktopAppInfo.new_from_filename(str(desktop_file)))

    def test_destdir_staging_and_uninstall_only_remove_owned_files(self):
        prefix = Path('/opt/chiterm home/.local')
        destdir = self.directory / 'package stage'
        staged_prefix = destdir / 'opt' / 'chiterm home' / '.local'
        install(prefix, destdir=destdir, source_root=REPOSITORY)
        desktop = staged_prefix / 'share' / 'applications' / 'chiterm.desktop'
        contents = desktop.read_text()
        self.assertIn(f'Exec="{prefix / "bin" / "chiterm"}"', contents)
        self.assertNotIn(str(destdir), contents)

        config = self.directory / 'user home' / '.config' / 'chiterm' / 'config.json'
        config.parent.mkdir(parents=True)
        config.write_text('{"theme":"paper-bloom"}\n')
        keep_binary = staged_prefix / 'bin' / 'keep-me'
        keep_binary.write_text('owned by another app')
        keep_data = staged_prefix / 'lib' / 'chiterm' / 'user-data.txt'
        keep_data.write_text('not an installer file')
        other_desktop = staged_prefix / 'share' / 'applications' / 'other.desktop'
        other_desktop.write_text('[Desktop Entry]\nName=Other\n')

        removed = uninstall(prefix, destdir=destdir)

        self.assertEqual(len(removed), len(RUNTIME_FILES) + 2)
        self.assertTrue(all(not path.exists() for path in removed))
        self.assertEqual(config.read_text(), '{"theme":"paper-bloom"}\n')
        self.assertTrue(keep_binary.exists())
        self.assertTrue(keep_data.exists())
        self.assertTrue(other_desktop.exists())

    def test_desktop_exec_supports_spaces_and_rejects_ambiguous_characters(self):
        argument = '/tmp/a path/chiterm'
        self.assertEqual(desktop_exec_quote(argument), f'"{argument}"')
        with self.assertRaises(ValueError):
            desktop_exec_quote('/tmp/bad\npath')
        for character in ('\\', '"', "'", '$', '`', '%', ';', '*', '\t'):
            with self.subTest(character=character), self.assertRaises(ValueError):
                desktop_exec_quote(f'/tmp/path{character}name')

    def test_rejected_desktop_path_does_not_partially_install(self):
        prefix = self.directory / 'home' / 'percent%prefix'
        with self.assertRaises(ValueError):
            install(prefix, source_root=REPOSITORY)
        self.assertFalse(prefix.exists())

    def test_running_installer_twice_updates_known_files(self):
        prefix = self.directory / 'local'
        install(prefix, source_root=REPOSITORY)
        original = (prefix / 'lib' / 'chiterm' / 'version.py').read_text()
        (prefix / 'lib' / 'chiterm' / 'version.py').write_text('old version')
        install(prefix, source_root=REPOSITORY)
        self.assertEqual((prefix / 'lib' / 'chiterm' / 'version.py').read_text(), original)


if __name__ == '__main__':
    unittest.main()
