.PHONY: setup ensure-venv test e2e unit run one lint help

VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

help:
	@echo "Available targets:"
	@echo "  make setup  - create .venv and install dependencies"
	@echo "  make test   - compile + unit + voice smoke"
	@echo "  make unit   - unit tests only"
	@echo "  make e2e    - run manual E2E scenario"
	@echo "  make run    - one-command app start"
	@echo "  make one    - alias for make run"

run: ensure-venv
	VIRTUAL_ENV=$(PWD)/$(VENV) PATH=$(PWD)/$(VENV)/bin:$$PATH bash scripts/run_app.sh .env.test

one: run

ensure-venv:
	@if [ ! -x "$(PYTHON)" ]; then \
		echo "[info] .venv not found. Running setup..."; \
		$(MAKE) setup; \
	fi

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

test: ensure-venv
	VIRTUAL_ENV=$(PWD)/$(VENV) PATH=$(PWD)/$(VENV)/bin:$$PATH bash scripts/run_tests.sh

unit: ensure-venv
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

e2e: ensure-venv
	VIRTUAL_ENV=$(PWD)/$(VENV) PATH=$(PWD)/$(VENV)/bin:$$PATH bash scripts/run_e2e_manual.sh .env.test

lint: ensure-venv
	PYTHONPATH=src $(PYTHON) -m ruff check src tests
