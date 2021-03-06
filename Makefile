VENV := ./.venv
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

.PHONY:setup
setup: venv install ## setting Python for the project

sourcedata/anzeigen.zip: ## Download the source data for the project
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
	$(PYTHON) utils.py rename_xml_files

.PHONY: check_s3
check_s3: ## Check if configured s3 already exist and create them if needed
	$(PYTHON) utils.py check_s3

.PHONY: list_s3
list_s3: ## List data from configured s3 buckets
	$(PYTHON) utils.py list_s3

.PHONY: delete_s3
delete_s3: ## Delete configured s3 buckets
	$(PYTHON) utils.py delete_s3

.PHONY: process_xml
process_xml: ## Extract data from ALTO xml to json
	$(PYTHON) process_xml.py

.PHONY: process_scans
process_scans: ## Create thumbnail and smaller version of scanned page
	$(PYTHON) process_scans.py

.PHONY: process_ads
process_ads: ## Create images of single advertisments elements
	$(PYTHON) process_ads.py

.PHONY: zip_output
zip_output: datafolder ## Put output content in a zip archive
	$(PYTHON) utils.py zip_output

.PHONY: pipeline
pipeline: sourcedata/anzeigen.zip datafolder rename_xml_files check_s3 process_xml process_scans process_ads  zip_output  ## run the data transformation

.PHONY: full-pipeline
full-pipeline: setup pipeline  ## run the data transformation

.PHONY: tests
tests: ## Run tests for python scripts
	pytest

.PHONY: clean
clean: ## Remove material folder (scans and alto xml files)
	rm -rf datafolder
	rm -rf output
	rm -rf output.zip
