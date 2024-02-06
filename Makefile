help:
	@echo "lint - lint code"
	@echo "install-dev - install all dependencies for development"
	@echo "test - run tests"

install-dev:
	poetry install --with dev,test --all-extras

lint:
	@ERROR=0; \
	poetry run isort . || ERROR=1; \
	poetry run black .  || ERROR=1; \
	poetry run pydocstyle . || ERROR=1; \
	poetry run yamllint -c yamllint.yaml . || ERROR=1; \
	poetry run mypy . || ERROR=1; \
	poetry run pre-commit run --all || ERROR=1; \
	exit $$ERROR
	# TODO: fix pylint to discover all projects \
	# poetry run pylint aineko || ERROR=1; \

test:
	pytest . -sv
