"""Pure command palette catalog and filtering; this module does not import GTK."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    label: str
    action: str
    keywords: tuple[str, ...] = ()
    shortcut: str = ''
    target: str | int | None = None


# Accelerator syntax is kept beside its display label so the command panel and
# GTK action registrations stay in sync.
ACTION_SHORTCUTS = {
    'new-tab': (('<Control><Shift>t',), 'Ctrl+Shift+T'),
    'close-pane': (('<Control><Shift>w',), 'Ctrl+Shift+W'),
    'split-right': (('<Control><Shift>d',), 'Ctrl+Shift+D'),
    'split-down': (('<Control><Shift>e',), 'Ctrl+Shift+E'),
    'copy': (('<Control><Shift>c',), 'Ctrl+Shift+C'),
    'paste': (('<Control><Shift>v',), 'Ctrl+Shift+V'),
    'find': (('<Control><Shift>f',), 'Ctrl+Shift+F'),
    'find-next': (('<Control><Shift>g',), 'Ctrl+Shift+G'),
    'find-previous': (('<Control><Shift><Alt>g',), 'Ctrl+Shift+Alt+G'),
    'next-pane': (('<Control><Shift>bracketright',), 'Ctrl+Shift+]'),
    'previous-pane': (('<Control><Shift>bracketleft',), 'Ctrl+Shift+['),
    'toggle-pane-zoom': (('<Control><Shift>Return',), 'Ctrl+Shift+Enter'),
    'next-tab': (('<Control>Page_Down',), 'Ctrl+Page Down'),
    'previous-tab': (('<Control>Page_Up',), 'Ctrl+Page Up'),
    # Keep both common plus-key layouts supported.
    'zoom-in': (('<Control>plus', '<Control>equal'), 'Ctrl++ / Ctrl+='),
    'zoom-out': (('<Control>minus',), 'Ctrl+-'),
    'zoom-reset': (('<Control>0',), 'Ctrl+0'),
    'command-palette': (('<Control><Shift>p',), 'Ctrl+Shift+P'),
}


_ACTIONS = (
    ('New Tab', 'new-tab', ('new', 'tab', '标签', '新建')),
    ('Split Left / Right', 'split-right', ('split', 'horizontal', '分屏', '左右')),
    ('Split Top / Bottom', 'split-down', ('split', 'vertical', '分屏', '上下')),
    ('Close Pane or Tab', 'close-pane', ('close', 'pane', 'tab', '关闭', '面板', '标签')),
    ('Copy', 'copy', ('clipboard', 'selection', '复制', '剪贴板')),
    ('Paste', 'paste', ('clipboard', '粘贴', '剪贴板')),
    ('Find in Pane', 'find', ('search', 'scrollback', 'find', '搜索', '查找', '滚动回看')),
    ('Next Match', 'find-next', ('search', 'next', 'match', '下一个', '结果')),
    ('Previous Match', 'find-previous', ('search', 'previous', 'match', '上一个', '结果')),
    ('Next Pane', 'next-pane', ('focus', 'navigate', '下一个', '面板', '切换')),
    ('Previous Pane', 'previous-pane', ('focus', 'navigate', '上一个', '面板', '切换')),
    ('Zoom or Restore Pane', 'toggle-pane-zoom', ('maximize', 'zoom', 'pane', '最大化', '恢复', '面板')),
    ('Rename Current Tab', 'rename-tab', ('tab', 'title', 'name', '重命名', '标签', '标题')),
    ('Next Tab', 'next-tab', ('switch', 'tab', '下一个', '标签', '切换')),
    ('Previous Tab', 'previous-tab', ('switch', 'tab', '上一个', '标签', '切换')),
    ('Zoom In', 'zoom-in', ('font', 'text', 'increase', '字体', '放大')),
    ('Zoom Out', 'zoom-out', ('font', 'text', 'decrease', '字体', '缩小')),
    ('Reset Font Size', 'zoom-reset', ('font', 'text', 'reset', '字体', '重置')),
)


def build_commands(tabs=(), themes=()):
    """Build the current action, theme, and tab command list.

    ``tabs`` contains ``(stable_token, title)`` pairs. ``themes`` contains
    ``(theme_id, display_name)`` pairs. Both inputs are UI-independent values.
    """
    commands = [
        Command(label, action, keywords,
                ACTION_SHORTCUTS.get(action, ((), ''))[1])
        for label, action, keywords in _ACTIONS
    ]
    for theme_id, name in themes:
        tone = '浅色' if theme_id in ('paper-bloom', 'sage-ledger') else '深色'
        commands.append(Command(
            f'Theme: {name}', 'theme', ('theme', 'palette', 'color', '配色', '颜色', tone),
            target=theme_id))
    for index, (token, title) in enumerate(tabs, start=1):
        commands.append(Command(
            f'Switch to Tab {index}: {title}', 'select-tab',
            ('tab', 'switch', 'project', '标签', '切换', title), target=token))
    return commands


def filter_commands(commands, query):
    """Filter commands by case-insensitive all-token substring matching."""
    terms = query.casefold().split()
    if not terms:
        return list(commands)
    matches = []
    for command in commands:
        searchable = ' '.join((command.label, *command.keywords, command.shortcut)).casefold()
        words = searchable.split()
        if all((term in searchable if len(term) > 1 or not term.isascii()
                else term in words) for term in terms):
            matches.append(command)
    return matches
