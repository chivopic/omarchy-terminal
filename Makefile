PYTHON ?= /usr/bin/python3

.PHONY: check test-gui test-all

# Fast checks that run without a graphical display.
check:
	$(PYTHON) -m py_compile chiterm.py terminal_links.py terminal_search.py tests/*.py
	$(PYTHON) -m unittest discover -s tests -p 'test_terminal_search.py' -v
	$(PYTHON) -m unittest discover -s tests -p 'test_terminal_links.py' -v

# REQUIRE_GUI_TESTS makes a missing display a failure instead of a skip.
test-gui:
	REQUIRE_GUI_TESTS=1 $(PYTHON) -m unittest discover -s tests -p 'test_terminal_window.py' -v

test-all:
	$(MAKE) check
	$(MAKE) test-gui
