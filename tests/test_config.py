"""Isolated tests for Chiterm's XDG config storage."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from config import ConfigStore, config_path
from themes import DEFAULT_THEME, THEMES


class ConfigPathTests(unittest.TestCase):
    def test_uses_absolute_xdg_config_home(self):
        path = config_path({'XDG_CONFIG_HOME': '/tmp/chiterm-config'}, home='/home/tester')
        self.assertEqual(path, Path('/tmp/chiterm-config/chiterm/config.json'))

    def test_ignores_relative_xdg_config_home(self):
        path = config_path({'XDG_CONFIG_HOME': 'relative/config'}, home='/home/tester')
        self.assertEqual(path, Path('/home/tester/.config/chiterm/config.json'))


class ConfigStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.path = self.directory / 'config.json'
        self.store = ConfigStore(self.path)

    def test_missing_or_invalid_config_falls_back_to_default(self):
        self.assertEqual(self.store.load_theme(), DEFAULT_THEME)
        invalid_values = (
            '{',
            json.dumps({'theme': 'unrecognized'}),
            json.dumps({'theme': DEFAULT_THEME, 'extra': True}),
            json.dumps(['theme', DEFAULT_THEME]),
        )
        for contents in invalid_values:
            with self.subTest(contents=contents):
                self.path.write_text(contents, encoding='utf-8')
                self.assertEqual(self.store.load_theme(), DEFAULT_THEME)

    def test_save_and_load_round_trip(self):
        theme_id = next(theme for theme in THEMES if theme != DEFAULT_THEME)
        self.store.save_theme(theme_id)
        self.assertEqual(self.store.load_theme(), theme_id)
        self.assertEqual(json.loads(self.path.read_text(encoding='utf-8')), {'theme': theme_id})
        self.assertEqual(list(self.directory.iterdir()), [self.path])

    def test_save_rejects_unknown_theme_without_touching_disk(self):
        with self.assertRaises(ValueError):
            self.store.save_theme('../unknown')
        self.assertFalse(self.path.exists())

    def test_failed_replace_keeps_old_config_and_removes_temporary_file(self):
        self.path.write_text(json.dumps({'theme': DEFAULT_THEME}), encoding='utf-8')
        with patch('config.os.replace', side_effect=OSError('simulated replace failure')):
            with self.assertRaises(OSError):
                self.store.save_theme(next(theme for theme in THEMES if theme != DEFAULT_THEME))
        self.assertEqual(self.store.load_theme(), DEFAULT_THEME)
        self.assertEqual(list(self.directory.iterdir()), [self.path])


if __name__ == '__main__':
    unittest.main()
