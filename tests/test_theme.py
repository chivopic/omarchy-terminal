import tempfile
import unittest
from pathlib import Path

from chiterm_theme import PALETTE_KEYS, read_theme


class ThemeTests(unittest.TestCase):
    def test_reads_complete_palette_in_terminal_color_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'colors.toml'
            path.write_text('\n'.join(f'{key} = "#{index:02x}0000"' for index, key in enumerate(PALETTE_KEYS)))
            foreground, background, palette = read_theme(path)
            self.assertAlmostEqual(background.red, 0.0)
            self.assertAlmostEqual(foreground.red, 7 / 255, places=4)
            self.assertEqual(len(palette), 16)
            self.assertAlmostEqual(palette[15].red, 15 / 255, places=4)

    def test_missing_malformed_and_partial_themes_use_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'colors.toml'
            self.assertIsNone(read_theme(path))
            path.write_text('not = [valid')
            self.assertIsNone(read_theme(path))
            path.write_text('background = "#000000"')
            self.assertIsNone(read_theme(path))
            path.write_text('\n'.join(f'{key} = "bad color"' for key in PALETTE_KEYS))
            self.assertIsNone(read_theme(path))


if __name__ == '__main__':
    unittest.main()
