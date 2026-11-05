"""Verify diagnostics work before importing optional GTK bindings."""
from pathlib import Path
import subprocess
import sys
import unittest

from version import VERSION


REPOSITORY = Path(__file__).resolve().parents[1]


class DiagnosticsTests(unittest.TestCase):
    def run_without_site_packages(self, flag):
        return subprocess.run(
            [sys.executable, '-S', str(REPOSITORY / 'chiterm.py'), flag],
            cwd=Path('/'), capture_output=True, text=True, check=False)

    def test_version_does_not_require_gi_or_a_display(self):
        result = self.run_without_site_packages('--version')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), VERSION)

    def test_check_reports_missing_bindings_without_a_traceback(self):
        result = self.run_without_site_packages('--check')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Python:', result.stdout)
        self.assertIn('GTK: unavailable', result.stdout)
        self.assertIn('VTE: unavailable', result.stdout)
        self.assertIn('Install python-gobject', result.stdout)
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
