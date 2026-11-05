PYTHON ?= /usr/bin/python3
PREFIX ?= $(HOME)/.local
DESTDIR ?=

.PHONY: check test-gui test-all install uninstall

# Fast checks that run without a graphical display.
check:
	$(PYTHON) -m py_compile *.py tests/*.py
	SKIP_GUI_TESTS=1 $(PYTHON) -m unittest discover -s tests -v

# REQUIRE_GUI_TESTS makes a missing display a failure instead of a skip.
test-gui:
	REQUIRE_GUI_TESTS=1 $(PYTHON) -m unittest discover -s tests -p 'test_terminal_window.py' -v

test-all:
	$(MAKE) check
	$(MAKE) test-gui

install:
	$(PYTHON) install.py --prefix "$(PREFIX)" $(if $(strip $(DESTDIR)),--destdir "$(DESTDIR)",)

uninstall:
	$(PYTHON) install.py --uninstall --prefix "$(PREFIX)" $(if $(strip $(DESTDIR)),--destdir "$(DESTDIR)",)
