.PHONY: quick-start install \
lint pre-commit test seed \
start-model stop-model down \
clean clean-buster full-clean help

## Show available commands in this Makefile
help:
	@echo ""
	@echo " - Setup & Installation - "
	@echo "  quick-start     Preps everything for app to run for the 1st time"
	@echo "  install         Reinstalls buster CLI after changes in source"
	@echo ""
	@echo " - Code Quality & Testing - "
	@echo "  lint            Runs ruff formatter and linter"
	@echo "  pre-commit      Runs pre-commit hooks across all files"
	@echo "  test            Runs full test suite using pytest"
	@echo "  seed            Writes 32 bust .md files to .buster/ for manual review"
	@echo ""
	@echo " - Model & Containers - "
	@echo "  start-model     Starts Ollama container and runs AI Model"
	@echo "  stop-model      Stops the Ollama container"
	@echo "  down            Stops all containers"
	@echo ""
	@echo " - Cleanup - "
	@echo "  clean           Removes python cache and build artefacts"
	@echo "  clean-buster    Removes user data directory, including DB"
	@echo "  full-clean      Removes everything, for a fresh start"
	@echo ""

# Setup & Installation Commands

## Quick Start: Syncs dependencies, installs CLI tool, and runs 1st time setup
quick-start:
	uv sync --group dev
	uv tool install .
	buster setup

## Reinstalls buster CLI
## Run after making changes to files in source (src/)
install:
	uv tool install .

# Code Quality & Testing Commands

## Runs ruff formatter + linter (cache removed to ensure all files are checked)
lint:
	rm -rf .ruff_cache
	uv run ruff format && uv run ruff check

## Runs all pre-commit hooks across all files 
## Use before committing to git to ensure code quality
pre-commit:
	uv run pre-commit run --all-files

## Runs full test suite with pytest
## Ollama tests skipped if model is not running
test:
	uv run pytest tests/ -v

## Automatically generates 32 busts for seeding purposes
## Follows normal bust generation process, useful to review generation quality
seed:
	cd src/buster/AI && uv run seed.py

# Model & Containers Commands

## Start the Ollama container and pull qwen2.5:1.5b if not already present
start-model:
	docker compose up -d ollama
	docker compose exec ollama ollama pull qwen2.5:1.5b

## Stop the Ollama container
stop-model:
	docker compose stop ollama

## Stop all containers
down:
	docker compose down

# Cleanup Commands

## Remove cache and build artefacts
## Includes ruff, python, pytest caches and build dirs
clean:
	rm -rf .ruff_cache __pycache__ src/code_buster.egg-info \
	build/ dist/ .pytest_cache

## Remove the app (buster) data directory
## Includes all stored busts and settings (aka reset the app to fresh state)
clean-buster:
	rm -rf .buster

## Remove everything
## Previous clean commands + the virtual environment directory (.venv)
## Use for complete reset, as if freshly cloned with no setup done
full-clean: clean clean-buster
	rm -rf .venv
