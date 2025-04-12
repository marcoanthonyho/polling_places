# Define virtual environment name and paths
VENV = .venv
BIN = $(VENV)/bin
PIP = $(BIN)/pip
PYTHON = $(BIN)/python
DEPS_CHECK = $(VENV)/installed.txt
UV = $(BIN)/uv

DIRS = $(VENV) build dist wheels

# Define target for setting up the virtual environment and installing dependencies
.PHONY: setup install activate clean lint compile-requirements

$(DEPS_CHECK): requirements.txt $(UV)
	$(UV) pip install -e .[dev] -r requirements.txt --python=$(PYTHON)
	$(UV) pip freeze >$@
	@echo "Dependencies installed."
# Target to create and set up the virtual environment
$(VENV) $(PYTHON):
	python -m venv $(VENV) --upgrade-deps
	$(PIP) install --upgrade pip
	@echo "Virtual environment created in $(VENV)"

$(UV): $(VENV)
	$(PIP) install uv pip-tools

# Target to install dependencies from requirements.txt
dev: $(VENV) $(DEPS_CHECK)

# Target to activate the virtual environment (use this after running 'make setup')
activate:
	@echo "To activate the virtual environment, run:"
	@echo "source $(VENV)/bin/activate"

# Target to clean up and remove the virtual environment
clean:
	rm -rf $(VENV)
	@echo "Virtual environment removed."

# Target to run pre-commit hooks
lint:
	pre-commit run --all-files

# Target to compile requirements.txt from requirements.in
pip-compile:
	$(VENV)/bin/uv pip compile --output-file=requirements.txt requirements.in
	@echo "requirements.txt compiled from requirements.in"