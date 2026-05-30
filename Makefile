.PHONY: quick-start install lint pre-commit test seed start-model stop-model down clean clean-buster full-clean help

## Show available commands in this Makefile
help:
	@echo ""
	@echo " - Setup & Installation - "
	@echo "  quick-start     Preps everything for app to run for the 1st time"
	@echo "  install         Reinstalls Buster CLI after any source change"
	@echo ""
	@echo " - Code Quality & Testing - "
	@echo "  lint            Runs ruff formatter and linter"
	@echo "  pre-commit      Runs pre-commit hooks"
	@echo "  test            Runs the full test suite"
	@echo "  seed            Seeds the database with example busts"
	@echo ""
	@echo " - Model & Containers - "
	@echo "  start-model     Starts Ollama container and runs qwen2.5:1.5b"
	@echo "  stop-model      Stops the Ollama container"
	@echo "  down            Stops all containers"
	@echo ""
	@echo " - Cleanup - "
	@echo "  clean           Removes python cache and build artefacts"
	@echo "  clean-buster    Removes .buster directory and all stored data"
	@echo "  full-clean      Removes everything, including .venv"
	@echo ""

# Setup & Installation Commands

## Quick Start: Syncs dependencies, installs the CLI tool, and runs the first-time setup
quick-start:
	uv sync --group dev
	uv tool install .
	buster setup

## Reinstall the buster CLI tool locally (use after making changes to source code)
install:
	uv tool install .

# Code Quality & Testing Commands

## Run ruff formatter and linter (cache removed to ensure all files are checked)
lint:
	rm -rf .ruff_cache
	uv run ruff format && uv run ruff check

## Run all pre-commit hooks across all files (use before committing to ensure code quality)
pre-commit:
	uv run pre-commit run --all-files

## Run full test suite with pytest — Ollama tests skipped if model not running
## Run 'make start-model' first to include the full pipeline tests
test:
	uv run pytest tests/ -v

## Seed the database with 32 example incidents via the Buster crew
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

## Remove cache and build artefacts (ruff, python, pytest caches and build dirs)
clean:
	rm -rf .ruff_cache __pycache__ src/code_buster.egg-info build/ dist/ .pytest_cache

## Remove the app (buster) data directory, including all stored busts and settings (aka reset the app to fresh state)
clean-buster:
	rm -rf .buster

## Remove everything: venv, caches, build artefacts, and stored data (use before a fresh quick-start)
full-clean:
	rm -rf .venv .ruff_cache __pycache__ src/code_buster.egg-info build/ dist/ .pytest_cache .buster
