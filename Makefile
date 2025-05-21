lint:
	@echo
	isort --diff -c --skip-glob '*.venv' --skip app.py .
	@echo
	black --exclude '(\.venv|app\.py)' .
	@echo
	flake8 --exclude app.py,.venv .
	@echo
	mypy --ignore-missing-imports --exclude '(\.venv/|app\.py)' .


format_code:
	isort --skip app.py .
	black --exclude '(\.venv|app\.py)' .
	flake8 --exclude app.py,.venv .


test:
	pytest -vvv --cov-report term-missing --cov-report html --cov-branch \
			--cov fastapi_mail/
