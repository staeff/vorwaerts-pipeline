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
install: ## Make venv and install requirements
	$(VENV)/bin/pip install -r requirements.txt

sourcedata: ## Download the source data for the project
	@# -p silences the cmd, if folder already exists
	@mkdir -p sourcedata
	echo 'Downloading source files (964 MB)'
	curl https://download.codingdavinci.de/s/7rTJnf5dP3nKJYp/download -o sourcedata/anzeigen.zip

datafolder: sourcedata ## Unzip downloaded data and put into right folder structure
	unzip sourcedata/anzeigen.zip -d datafolder
	mv datafolder/Kleinanzeigen\ aus\ dem\ \"Vorwärts\"/Mediendateien datafolder/images
	mv datafolder/Kleinanzeigen\ aus\ dem\ \"Vorwärts\"/OCR/Alto-XML datafolder/xml
	mv datafolder/Kleinanzeigen\ aus\ dem\ \"Vorwärts\"/Metadaten/vorwaerts-metadaten.csv datafolder/metadaten.csv
	rm -rf datafolder/Kleinanzeigen\ aus\ dem\ \"Vorwärts\"/

.PHONY: rename_xml_files
rename_xml_files: datafolder ## Rename xml files
	$(PYTHON) rename_xml_files.py

.PHONY: tests ## Run tests for python scripts
tests:
	pytest

.PHONY: json ## Run tests for python scripts
json:
	$(PYTHON) process_xml.py

.PHONY: diff ## Run tests for python scripts
diff:
	jq . advertisments.json > new.json
	jq . advertisments_base.json > old.json
	vimdiff new.json old.json

.PHONY:setup
setup: sourcedata datafolder rename_xml_files ## setting up the project

.PHONY: clean
clean: ## Remove material folder (scans and alto xml files)
	rm -rf datafolder
