PYTHON ?= python

.PHONY: all
all: format check

.PHONY: check
check: check-pylint check-mypy check-black

.PHONY: check-pylint
check-pylint:
	$(PYTHON) -m pylint src

.PHONY: check-mypy
check-mypy:
	$(PYTHON) -m mypy src

.PHONY: check-black
check-black:
	$(PYTHON) -m black --check src

.PHONY: format
format:
	$(PYTHON) -m black src

.PHONY: build
build:
	$(PYTHON) -m build

.PHONY: upload
upload:
	$(PYTHON) -m twine upload -u __token__ dist/*

.PHONY: docs
docs:
	$(MAKE) -C docs html
