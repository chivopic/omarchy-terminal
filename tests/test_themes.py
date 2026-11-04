"""Pure Python checks for built-in terminal palettes."""
import unittest

from themes import DEFAULT_THEME, THEMES


def luminance(color):
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045
              else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return sum(weight * channel for weight, channel in zip((0.2126, 0.7152, 0.0722), linear))


def contrast(foreground, background):
    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class ThemeTests(unittest.TestCase):
    def test_four_custom_themes_cover_dark_and_light_backgrounds(self):
        self.assertGreaterEqual(len(THEMES), 4)
        self.assertIn(DEFAULT_THEME, THEMES)
        backgrounds = [luminance(theme.background) for theme in THEMES.values()]
        self.assertGreaterEqual(sum(value < 0.2 for value in backgrounds), 2)
        self.assertGreaterEqual(sum(value > 0.8 for value in backgrounds), 2)

    def test_every_theme_has_sixteen_valid_ansi_colors(self):
        for theme_id, theme in THEMES.items():
            with self.subTest(theme=theme_id):
                self.assertEqual(len(theme.ansi), 16)
                for color in (theme.foreground, theme.background, theme.cursor,
                              theme.selection_foreground, theme.selection_background,
                              *theme.ansi):
                    self.assertRegex(color, r'^#[0-9a-fA-F]{6}$')

    def test_text_and_selection_meet_wcag_aa_contrast(self):
        for theme_id, theme in THEMES.items():
            with self.subTest(theme=theme_id):
                self.assertGreaterEqual(contrast(theme.foreground, theme.background), 4.5)
                self.assertGreaterEqual(
                    contrast(theme.selection_foreground, theme.selection_background), 4.5)
                for index, color in enumerate(theme.ansi):
                    with self.subTest(ansi=index):
                        self.assertGreaterEqual(contrast(color, theme.background), 3.0)


if __name__ == '__main__':
    unittest.main()
