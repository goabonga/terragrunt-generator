PY = python3
VENV = .venv
BIN=$(VENV)/bin

all: lint test

$(VENV): setup.py
	$(PY) -m venv $(VENV)
	$(BIN)/pip install -e .[dev]
	touch $(VENV)

.PHONY:
test: $(VENV)
	$(BIN)/pytest --cov-config=.coveragerc --cov --cov-report=json --cov-report=term --cov-report=html -vv

.PHONY: lint
lint: $(VENV)
	$(BIN)/isort ./generator ./tests
	$(BIN)/black ./generator ./tests
	$(BIN)/flake8 ./generator ./tests

.PHONY: release
release: $(VENV)
	$(BIN)/python setup.py sdist bdist_wheel upload

clean:
	rm -fr $(VENV)/
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
