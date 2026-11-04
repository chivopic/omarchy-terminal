"""Search option and pattern tests, with no GTK/VTE dependency."""
import re
import unittest

from terminal_search import (
    SEARCH_CASELESS,
    SEARCH_FLAGS,
    SearchCaseMode,
    build_search_pattern,
)


class TerminalSearchTests(unittest.TestCase):
    def test_literal_queries_escape_regular_expression_characters(self):
        query = 'value v1.2 [ready] (done)'
        pattern, _flags = build_search_pattern(query)
        self.assertEqual(pattern, re.escape(query))
        self.assertEqual(re.fullmatch(pattern, query).group(), query)
        self.assertIsNone(re.fullmatch(pattern, 'value v1x2 [ready] (done)'))

    def test_smart_case_uses_uppercase_letters_to_choose_sensitivity(self):
        _, lower_flags = build_search_pattern('response')
        _, mixed_flags = build_search_pattern('Response')
        self.assertTrue(lower_flags & SEARCH_CASELESS)
        self.assertFalse(mixed_flags & SEARCH_CASELESS)
        self.assertEqual(lower_flags & ~SEARCH_CASELESS, SEARCH_FLAGS)

    def test_explicit_case_modes_override_smart_case(self):
        _, sensitive_flags = build_search_pattern('lower', SearchCaseMode.SENSITIVE)
        _, insensitive_flags = build_search_pattern('UPPER', SearchCaseMode.INSENSITIVE)
        self.assertFalse(sensitive_flags & SEARCH_CASELESS)
        self.assertTrue(insensitive_flags & SEARCH_CASELESS)

    def test_regex_mode_preserves_the_supplied_expression(self):
        expression = r'item\s+\d+'
        pattern, _flags = build_search_pattern(expression, use_regex=True)
        self.assertEqual(pattern, expression)

    def test_invalid_case_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            build_search_pattern('query', 99)


if __name__ == '__main__':
    unittest.main()
