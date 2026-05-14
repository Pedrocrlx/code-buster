PHONY: up down clean

up: # Build and start the containers
	docker compose up --build

down: # Stop the containers
	docker compose down 

clean: # Stop the containers and remove volumes and orphan containers
	docker compose down -v --remove-orphans

