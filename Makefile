PHONY: up down clean ollama pull

up: # Build and start the containers
	docker compose up --build

down: # Stop the containers
	docker compose down 

clean: # Stop the containers and remove volumes and orphan containers
	docker compose down -v --remove-orphans

pull: # Pull the required Ollama model (qwen2.5:1.5b)
	ollama pull qwen2.5:1.5b

ollama: # Run the Ollama AI agent script
	uv run python config/ai/ai.py

