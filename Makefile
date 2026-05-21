.PHONY: up down clean start-model stop-model analyze

up: # Build and start the containers
	docker compose up --build

down: # Stop the containers
	docker compose down

clean: # Stop the containers and remove volumes and orphan containers
	docker compose down -v --remove-orphans

start-model: # Start the Ollama container and pull the model
	docker compose up -d ollama
	docker compose exec ollama ollama pull qwen2.5:1.5b

stop-model: # Stop the Ollama container
	docker compose stop ollama

bust: # Run the Root Cause Analyst (prompts for incident description)
	cd buster && uv run buster

