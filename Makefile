VENV ?= venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
REQ_DEV := requirements-dev.txt
REQ := requirements.txt
TEST_DIR := tests

.PHONY: help venv install install-prod test coverage coverage-html lint format isort clean run activate

help:
	@echo "Makefile targets:"
	@echo "  venv          - create virtualenv in $(VENV)"
	@echo "  install        - create venv and install $(REQ_DEV)"
	@echo "  install-prod   - create venv and install $(REQ)"
	@echo "  test           - run pytest for $(TEST_DIR)"
	@echo "  coverage       - run tests and print coverage report"
	@echo "  coverage-html  - run tests and generate htmlcov/"
	@echo "  lint           - run flake8"
	@echo "  format         - run black + isort on src and tests"
	@echo "  clean          - remove venv, caches and coverage artifacts"
	@echo "  run            - run the package entrypoint (python -m src)"
	@echo "  activate       - print activation command for this shell"

venv:
	@test -d $(VENV) || python3 -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools

install: venv
	$(PIP) install -r $(REQ_DEV)

install-prod: venv
	$(PIP) install -r $(REQ)

test: venv
	$(PYTHON) -m pytest $(TEST_DIR) $(pytest_args)

coverage: venv
	$(PYTHON) -m coverage run -m pytest $(TEST_DIR)
	$(PYTHON) -m coverage report -m

coverage-html: venv
	$(PYTHON) -m coverage run -m pytest $(TEST_DIR)
	$(PYTHON) -m coverage html
	@echo "Open htmlcov/index.html to view the report"

lint: venv
	$(PYTHON) -m flake8

format: venv
	$(PYTHON) -m isort src $(TEST_DIR)
	$(PYTHON) -m black src $(TEST_DIR)

isort: venv
	$(PYTHON) -m isort src $(TEST_DIR)

clean:
	@echo "Cleaning project artifacts..."
	-rm -rf $(VENV)
	-rm -rf .pytest_cache htmlcov .coverage
	-find . -type d -name __pycache__ -print -exec rm -rf {} +

run: venv
	$(PYTHON) -m src

activate:
	@echo "To activate the virtualenv in your shell run:"
	@echo "  source $(VENV)/bin/activate"
