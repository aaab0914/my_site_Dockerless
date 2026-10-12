PYTHON ?= python
MANAGE := $(PYTHON) manage.py

.PHONY: help install install-dev run migrate makemigrations shell test check deploy-check typecheck schema docs format lint html-check clean

help:
	@echo "Available targets:"
	@echo "  install        Install production dependencies"
	@echo "  install-dev    Install project dependencies for development"
	@echo "  run            Start the Django development server"
	@echo "  migrate        Apply database migrations"
	@echo "  makemigrations Create new migrations"
	@echo "  shell          Open the Django shell"
	@echo "  test           Run the Django test suite"
	@echo "  check          Run Django system checks"
	@echo "  deploy-check   Run Django deployment checks"
	@echo "  typecheck      Run mypy with Django and DRF stubs"
	@echo "  schema         Generate and validate the OpenAPI schema"
	@echo "  docs           Open the API documentation URL"
	@echo "  format         Format Python files with Ruff"
	@echo "  lint           Run Ruff checks"
	@echo "  html-check     Check Django templates with djLint"

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev: install

run:
	$(MANAGE) runserver

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

shell:
	$(MANAGE) shell

test:
	$(MANAGE) test

check:
	$(MANAGE) check

deploy-check:
	$(MANAGE) check --deploy

typecheck:
	$(PYTHON) -m mypy blog users my_site

schema:
	$(MANAGE) spectacular --file schema.yml --validate

docs:
	@echo "Swagger UI: http://127.0.0.1:8000/api/docs/"
	@echo "ReDoc:       http://127.0.0.1:8000/api/redoc/"
	@echo "OpenAPI:     http://127.0.0.1:8000/api/schema/"

format:
	$(PYTHON) -m ruff format .

lint:
	$(PYTHON) -m ruff check .

html-check:
	$(PYTHON) -m djlint blog/templates users/templates --check

clean:
	$(PYTHON) -c "import pathlib, shutil; [p.unlink() for p in pathlib.Path('.').rglob('*.pyc')]; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__') if p.is_dir()]"
