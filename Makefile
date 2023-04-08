

dev: init
	./.venv/bin/pre-commit install
	./.venv/bin/pre-commit run

init:
	python -m venv .venv
	./.venv/bin/python -m pip install --upgrade pip
	./.venv/bin/python -m pip install -e ./\[dev\]

test:
	./.venv/bin/python -m pytest

lint:
	./.venv/bin/isort ./generator ./tests
	./.venv/bin/black ./generator ./tests
	./.venv/bin/flake8 ./generator ./tests
