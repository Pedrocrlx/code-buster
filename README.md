# Code Buster

A local-first CLI tool for developers to log coding incidents and recall past solutions — powered by AI agents running fully offline via Ollama. No data leaves your machine.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| CLI | [uv](https://docs.astral.sh/uv/) |
| AI agents | [CrewAI](https://github.com/crewAIInc/crewAI) |
| Local LLM | [Ollama](https://ollama.com/) — `qwen2.5:1.5b` |
| Container | [Docker](https://docs.docker.com/get-docker/) + Docker Compose |
| Database | SQLite |
| Linting | [Ruff](https://docs.astral.sh/ruff/) |
| Testing | [pytest](https://pytest.org/) |

## Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [uv](https://docs.astral.sh/uv/)

## Quick Start

**1. Clone and install dependencies:**
```bash
git clone <repo-url>
cd code-buster
uv sync --group dev
```

**2. Start the local AI model (first time only):**
```bash
make start-model
```

**3. Log your first incident:**
```bash
make bust
```

**4. Recall a past solution:**
```bash
make recall
```

## Usage

### `make bust` — Log an incident

Prompts you to describe what went wrong, what you tried, and whether it was resolved. The AI agents process the input and save a structured record to the local database.

```
$ make bust
What project were you working on?
> devcontainer setup

What was the issue you were facing?
> Docker daemon not running inside the devcontainer

What did you try to solve it?
> Mounted /var/run/docker.sock from the host

Did it work? (yes/no)
> yes

We are now processing your bust report... DONE!
We are now neatly organizing the information... DONE!
Everything Processed & Bust Saved! (Bust #1)
```

### `make recall` — Search past incidents

Prompts you to describe a problem you're facing. The agents search your knowledge base and narrate any relevant past incidents and how they were solved.

```
$ make recall
What problem are you facing right now?
> docker daemon won't connect inside my container

Searching your knowledge base... DONE!
Putting it into words... DONE!

You ran into the same issue with your devcontainer setup. Docker ps was
returning 'Cannot connect to the Docker daemon'. You tried mounting
/var/run/docker.sock from the host into the devcontainer, and that fixed it.
```

## Available Commands

| Command | Description |
|---|---|
| `make bust` | Log a new coding incident |
| `make recall` | Search past incidents for a solution |
| `make test` | Run the test suite |
| `make start-model` | Start the Ollama container and pull the model |
| `make stop-model` | Stop the Ollama container |
| `make ruff` | Run linter and formatter |
| `make down` | Stop all containers |

## Running Tests

Tests require Ollama running (`make start-model`). The DB and search tests run without it; the full pipeline tests are skipped automatically if Ollama is not available.

```bash
make test
```

---

## AI Usage

This project was built with assistance from **Claude Code (Anthropic)** throughout the development process.

| Area | Context | Tool | How it was used |
|---|---|
| CrewAI agent design | Designing and iterating on the agent pipeline, defining roles, goals, and task descriptions in YAML |
| CLI implementation | Building the interactive prompt flow, spinner animation with threading |
| Architecture | Separating bust and recall into independent crews with isolated config files |
| Bug fixing | Resolving CrewAI `@CrewBase` config conflicts between crews |
| Testing | Designing the integration test suite and `busted_db` fixture |
| Documentation | Scaffolding this README |
