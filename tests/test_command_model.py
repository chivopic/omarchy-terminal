"""Command catalog tests that need only the Python standard library."""
import unittest

from command_model import ACTION_SHORTCUTS, build_commands, filter_commands


class CommandModelTests(unittest.TestCase):
    def setUp(self):
        self.commands = build_commands(
            [('project-a', 'API Service'), ('project-b', 'Web 客户端')],
            [('midnight-fern', 'Midnight Fern'), ('paper-bloom', 'Paper Bloom')])

    def test_query_matches_localized_action_keywords(self):
        results = filter_commands(self.commands, '新建 标签')
        self.assertEqual([command.action for command in results], ['new-tab'])
        self.assertEqual([command.action for command in filter_commands(self.commands, '重命名')],
                         ['rename-tab'])

    def test_queries_find_themes_and_named_tabs(self):
        self.assertEqual([command.target for command in filter_commands(self.commands, '浅色 配色')],
                         ['paper-bloom'])
        tabs = filter_commands(self.commands, '切换 API')
        self.assertEqual([(command.action, command.target) for command in tabs],
                         [('select-tab', 'project-a')])
        self.assertEqual([command.target for command in filter_commands(self.commands, 'web 客户端')],
                         ['project-b'])

    def test_empty_query_lists_commands_and_shortcuts(self):
        results = filter_commands(self.commands, '  ')
        new_tab = next(command for command in results if command.action == 'new-tab')
        self.assertEqual(new_tab.shortcut, 'Ctrl+Shift+T')
        self.assertEqual(ACTION_SHORTCUTS['command-palette'][1], 'Ctrl+Shift+P')
        self.assertEqual(results, self.commands)

    def test_no_results_are_an_empty_list(self):
        self.assertEqual(filter_commands(self.commands, 'nonexistent action'), [])


if __name__ == '__main__':
    unittest.main()
