.PHONY: serve-model stop-model pull-model agent ruff

run-model: # Starts Ollama via Docker. Pulls the model if not present.
	docker rm -f ollama 2>/dev/null; docker run -d --name ollama -p 11434:11434 -v ollama_data:/root/.ollama ollama/ollama
	docker exec ollama ollama list | grep -q "qwen2.5:0.5b" || docker exec ollama ollama pull qwen2.5:0.5b

stop-model: # Stop and remove the Ollama container
	docker rm -f ollama

agent: # Run the AI agent
	uv run python config/ai/ai.py

ruff: # Lint and format
	uv run ruff check . && uv run ruff format .
