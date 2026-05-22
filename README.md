# Code Buster CLI

```uv tool install .```

This **command** allow you to install buster on context '.' via **uv**
so after that you can simply run:

```buster``` or ```buster --help```
# code-buster

A CLI tool for developers to log incidents and have them structured by local AI agents running fully offline via Ollama. No data leaves the machine.

## How it works

After setting up the Ollama container with the a minimal Qwen2.5 model, the user can run `make bust` to start the incident logging process. The CLI will prompt the user to describe the incident they faced while coding, including what went wrong, what they tried, and what ultimately worked. This will help the user reflect on the incident and extract learnings for the future. The input is then processed by a series of local AI agents (an analyst and an advisor) that (currently and temporarily) organize the information into a structured JSON record with a title, problem description, attempted solutions, a lesson learned, and search tags. The final record is saved to the `output/` directory for future reference, once again, temporarily, as the project evolves to it's final form.

## Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [uv](https://docs.astral.sh/uv/)

## Setup

**1. Start the Ollama container and pull the model (first time only):**
```bash
make start-model
```

**2. Log an incident:**
```bash
make bust
```

Reports are saved to `buster/output/` as `<project>_<YYYYMMDDHHmm>.json`.

## Available commands

| Command | Description |
|---|---|
| `make bust` | Run the incident logger CLI |
| `make start-model` | Start the Ollama container and pull the model |
| `make stop-model` | Stop the Ollama container |
| `make up` | Build and start all containers |
| `make down` | Stop all containers |
| `make clean` | Stop containers and remove volumes |

---

## AI Usage

This project was built with assistance from **Claude Code (Anthropic)** throughout the development process.

### How it was used


CrewAI agent design: Designing and iterating on the agent pipeline (from 4 agents down to 2), defining roles, goals, and task descriptions in YAML
CLI implementation: Building the interactive prompt flow, spinner animation with threading, and structured JSON output |
Refactoring: Decision in dead scaffolding, and simplifying the agent architecture
Documentation: Scaffolding this README, and then manually editing it for clarity and completeness.
