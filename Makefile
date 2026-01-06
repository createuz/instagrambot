# ========================
# Project configuration
# ========================
PROJECT_DIR := .
VENV := ./venv
PY := $(VENV)/bin/python
ALEMBIC := $(VENV)/bin/alembic
RUFF := $(VENV)/bin/ruff
MYPY := $(VENV)/bin/mypy

.DEFAULT_GOAL := help

# ========================
# Help
# ========================

.PHONY: help
help: ## Show available commands
	@awk 'BEGIN { \
		FS = ":.*##"; \
		printf "\nUsage:\n  make \033[36m<command>\033[0m\n\nCommands:\n"; \
	} \
	/^[a-zA-Z_-]+:.*?##/ { \
		printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 \
	}' $(MAKEFILE_LIST)

# ========================
# Code quality
# ========================

.PHONY: format
format: ## Format code with ruff
	@$(RUFF) format $(PROJECT_DIR)

.PHONY: lint
lint: ## Run ruff lint checks
	@$(RUFF) check $(PROJECT_DIR)

.PHONY: lint-fix
lint-fix: ## Fix lint issues automatically
	@$(RUFF) check $(PROJECT_DIR) --fix

.PHONY: typecheck
typecheck: ## Run mypy type checks
	@$(MYPY) $(PROJECT_DIR)

.PHONY: check
check: format lint typecheck ## Run all code quality checks

# ========================
# Database (Alembic)
# ========================

.PHONY: migration
migration: ## Create new database migration (use: make migration message="desc")
	@$(ALEMBIC) revision \
		--autogenerate \
		--rev-id $$($(PY) alembic/_get_revision_id.py) \
		-m "$(message)"

.PHONY: migrate
migrate: ## Apply database migrations
	@$(ALEMBIC) upgrade head

# ========================
# Run
# ========================

.PHONY: run
run: ## Run application
	@$(PY) main.py
