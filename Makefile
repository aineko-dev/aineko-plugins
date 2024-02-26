help:
	@echo "lint - lint code"
	@echo "install-dev - install all dependencies for development"
	@echo "test - run tests"

install-dev:
	poetry install --with dev,test,docs --all-extras

lint:
	@ERROR=0; \
	poetry run isort . || ERROR=1; \
	poetry run black .  || ERROR=1; \
	poetry run pydocstyle . || ERROR=1; \
	poetry run yamllint -c yamllint.yaml . || ERROR=1; \
	poetry run mypy . || ERROR=1; \
	poetry run pre-commit run --all || ERROR=1; \
	poetry run pylint $$(git ls-files "*.py" | grep -vE "/tests/" ) || ERROR=1; \
	exit $$ERROR

test:
	pytest . -sv --cov=aineko_plugins

view-docs:
	poetry run mkdocs serve --watch docs
