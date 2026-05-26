.PHONY: up down clean start-model stop-model analyze

db: # create the SQLite database file
	uv run typer main.py db

tool: # install the tool locally
	uv tool install .
down: # Stop the containers
	docker compose down

ruff: # run ruff format and check
	rm -rf .ruff_cache
	uv run ruff format && uv run ruff check

pre-commit: # run all pre-commit checks
	uv run pre-commit run --all-files

clean_buster_dir: # remove the .buster directory
	rm -rf .buster

clean: # clean all generated cache files and directories
	rm -rf .ruff_cache __pycache__

start-model: # Start the Ollama container and pull the model
	docker compose up -d ollama
	docker compose exec ollama ollama pull qwen2.5:1.5b

stop-model: # Stop the Ollama container
	docker compose stop ollama

bust: # Run the Root Cause Analyst (prompts for incident description, saves to busts/ as MD)
	cd src/buster/AI && uv run main.py

save: # Save a bust MD file to the database: make save FILE=busts/bust_....md
	cd src/buster/AI && uv run save.py ../../../$(FILE)

recall: # Search past incidents for a similar problem
	cd src/buster/AI && uv run recall.py

seed: # Seed the database with 32 realistic incidents via the Buster crew
	cd src/buster/AI && uv run seed.py

test: # Run the test suite
	uv run pytest tests/ -v
