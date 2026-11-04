"""XDG configuration for Chiterm's small set of user preferences."""
import json
import os
from pathlib import Path
import tempfile

from themes import DEFAULT_THEME, THEMES


def config_path(environ=None, home=None):
    """Return the Chiterm config path, honoring an absolute XDG_CONFIG_HOME."""
    environ = os.environ if environ is None else environ
    home = Path.home() if home is None else Path(home)
    config_home = environ.get('XDG_CONFIG_HOME')
    if config_home:
        candidate = Path(config_home)
        if candidate.is_absolute():
            return candidate / 'chiterm' / 'config.json'
    return home / '.config' / 'chiterm' / 'config.json'


class ConfigStore:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else config_path()

    def load_theme(self):
        """Load a known theme id; missing, malformed, or invalid data uses default."""
        try:
            settings = json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return DEFAULT_THEME
        if (not isinstance(settings, dict) or set(settings) != {'theme'}
                or not isinstance(settings['theme'], str)
                or settings['theme'] not in THEMES):
            return DEFAULT_THEME
        return settings['theme']

    def save_theme(self, theme_id):
        """Atomically save a valid theme id, cleaning up the temp file on failure."""
        if not isinstance(theme_id, str) or theme_id not in THEMES:
            raise ValueError(f'Unknown Chiterm theme: {theme_id!r}')

        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f'.{self.path.name}.', suffix='.tmp', dir=self.path.parent)
            temporary_path = Path(temporary_name)
            with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
                json.dump({'theme': theme_id}, stream, ensure_ascii=False)
                stream.write('\n')
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_path, self.path)
            temporary_path = None
        except BaseException:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except OSError:
                    pass
            raise
