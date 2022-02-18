VENV := ./.venv
APP_DIR := .
BIN := $(VENV)/bin
PYTHON := $(BIN)/python

.PHONY: help
help: ## Show this help
	@grep -Eh '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: ## Make a new virtual environment
	python3 -m venv .venv

.PHONY: install
install: venv ## Make venv and install requirements
	$(VENV)/bin/pip install -r requirements.txt

sourcedata: ## Download the source data for the project
	@# -p silences the cmd, if folder already exists
	@mkdir -p sourcedata
	echo 'Downloading source files (964 MB)'
	curl https://download.codingdavinci.de/s/7rTJnf5dP3nKJYp/download -o sourcedata/anzeigen.zip

.PHONY:setup
setup: sourcedata ## setting up the project

.PHONY: clean
clean: ## Clean project folder
	rm -rf $(VENV)
