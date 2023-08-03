

dev: init
	./.venv/bin/pre-commit install
	./.venv/bin/pre-commit run

init:
	python -m venv .venv
	./.venv/bin/python -m pip install --upgrade pip
	./.venv/bin/python -m pip install -e ./\[dev\]

test:
	./.venv/bin/python -m pytest --cov-config=.coveragerc --cov --cov-report=json --cov-report=term --cov-report=html -vv

lint:
	./.venv/bin/isort ./generator ./tests
	./.venv/bin/black ./generator ./tests
	./.venv/bin/flake8 ./generator ./tests
