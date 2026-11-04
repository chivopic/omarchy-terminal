"""Pure search pattern construction shared by the UI and unit tests."""
from enum import IntEnum
import re


class SearchCaseMode(IntEnum):
    SMART = 0
    SENSITIVE = 1
    INSENSITIVE = 2


# PCRE2 flags required by VTE: UTF, Unicode and multiline.
SEARCH_FLAGS = 0x00080000 | 0x00020000 | 0x00000400
SEARCH_CASELESS = 0x00000008


def build_search_pattern(query, case_mode=SearchCaseMode.SMART, use_regex=False):
    """Return a PCRE2 pattern and flags for a literal or regular-expression query."""
    case_mode = SearchCaseMode(case_mode)
    pattern = query if use_regex else re.escape(query)
    insensitive = (case_mode == SearchCaseMode.INSENSITIVE or
                   (case_mode == SearchCaseMode.SMART
                    and not any(char.isupper() for char in query)))
    flags = SEARCH_FLAGS | (SEARCH_CASELESS if insensitive else 0)
    return pattern, flags
