lint:
	@echo
	isort --diff -c --skip-glob '*.venv' .
	@echo
	black .
	@echo
	flake8 .
	@echo
	mypy --ignore-missing-imports .


format_code:
	isort .
	black .
	flake8 .


test:
	pytest -vvv --cov-report term-missing --cov-report html --cov-branch \
			--cov fastapi_mail/
