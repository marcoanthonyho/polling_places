# Virtual environment setup
VENV = .venv

ifeq ($(OS),Windows_NT)
    BIN = $(VENV)\Scripts
    ACTIVATE_CMD = $(BIN)\activate
    RM = rmdir /S /Q
    PIP = $(BIN)\pip.exe
    PYTHON = $(BIN)\python.exe
    UV = $(BIN)\uv.exe
else
    BIN = $(VENV)/bin
    ACTIVATE_CMD = source $(BIN)/activate
    RM = rm -rf
    PIP = $(BIN)/pip
    PYTHON = $(BIN)/python
    UV = $(BIN)/uv
endif

DEPS_CHECK = $(VENV)/installed.txt
DIRS = $(VENV) build dist wheels

.PHONY: dev activate clean lint pip-compile

# Dependency installation target
$(DEPS_CHECK): requirements.txt $(UV)
	$(UV) pip install -e .[dev] -r requirements.txt --python=$(PYTHON)
	$(UV) pip freeze > $@
	@echo "Dependencies installed."

# Virtual environment setup
$(VENV) $(PYTHON):
	python -m venv $(VENV) --upgrade-deps
	$(PIP) install --upgrade pip
	@echo "Virtual environment created in $(VENV)"

# Ensure uv is installed inside the venv
$(UV): $(VENV)
	$(PIP) install uv pip-tools

# Full dev environment setup
dev: $(VENV) $(DEPS_CHECK)

# Activation hint
activate:
	@echo "To activate the virtual environment, run:"
	@echo "$(ACTIVATE_CMD)"

# Clean the virtual environment
clean:
	$(RM) $(VENV)
	@echo "Virtual environment removed."

# Lint using pre-commit
lint:
	pre-commit run --all-files

# Compile requirements.txt from requirements.in
pip-compile: $(VENV) $(UV)
	$(UV) pip compile --output-file=requirements.txt requirements.in
	@echo "requirements.txt compiled from requirements.in"
