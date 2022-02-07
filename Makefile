
lint:
	poetry run mypy src
	poetry run flake8 --extend-ignore E501,E741 src | tac

test:
	poetry run pytest

build: lint test
	poetry build

publish: build
	poetry publish

shell:
	poetry run python
