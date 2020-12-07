format:
	poetry run black pydantic_generator/
	poetry run isort pydantic_generator/
test:
	poetry run tox -p auto
