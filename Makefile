.PHONY: up down clean serve pull ollama ruff

up: # Build and start the containers
	docker compose up --build

down: # Stop the containers
	docker compose down

clean: # Stop the containers and remove volumes and orphan containers
	docker compose down -v --remove-orphans

serve: # Start the Ollama daemon (keep this running in a separate terminal)
	ollama serve

pull: # Pull the required model — requires make serve to be running
	ollama pull qwen2.5:1.5b

ollama: # Run the AI agent script — requires make serve to be running
	uv run python config/ai/ai.py

ruff: # Lint and format the codebase
	uv run ruff check . && uv run ruff format .
