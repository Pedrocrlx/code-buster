# Code Buster

A local-first CLI tool for developers to log coding incidents and recall past solutions — powered by AI agents running fully offline via Ollama. No data leaves your machine.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| CLI | [Typer](https://typer.tiangolo.com/) + [uv](https://docs.astral.sh/uv/) |
| AI agents | [CrewAI](https://github.com/crewAIInc/crewAI) |
| Local LLM | [Ollama](https://ollama.com/) — `qwen2.5:1.5b` |
| Container | [Docker](https://docs.docker.com/get-docker/) + Docker Compose |
| Database | SQLite |
| Linting | [Ruff](https://docs.astral.sh/ruff/) |
| Testing | [pytest](https://pytest.org/) |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CLI  (Typer)                      │
│  setup · init · db · bust · save · recall           │
└───────────────────────┬─────────────────────────────┘
                        │
          ┌─────────────┴──────────────┐
          │                            │
┌─────────▼──────────┐     ┌──────────▼─────────┐
│   Buster Crew      │     │   Recall Crew       │
│  (CrewAI + Ollama) │     │  (CrewAI + Ollama)  │
│                    │     │                     │
│  processor agent   │     │  narrator agent     │
│  organizer agent   │     │                     │
│  → IncidentEntry   │     │  → prose narration  │
│    (Pydantic)      │     │                     │
└─────────┬──────────┘     └──────────┬──────────┘
          │                            │
          │        ┌───────────────────┘
          ▼        ▼
┌──────────────────────────────────────────────────────┐
│                 Data Layer  (SQLite)                  │
│  save_bust · fetch_all_busts · search_by_tags        │
│  extract_keywords · stop-word filtering              │
└──────────────────────────────────────────────────────┘
```

**Bust flow** — the developer describes an incident at the CLI. The Buster crew runs two agents in sequence: `processor` extracts the problem and solutions from free text; `organizer` structures them into a validated Pydantic model. The result is written as a `.md` file for the developer to review, then saved to SQLite via `buster save`.

**Recall flow** — the developer describes a current problem. `extract_keywords` strips stop words and searches the database by tag overlap. Matching incidents are passed to the Recall crew's `narrator` agent, which produces a short conversational summary of what happened before and what worked.

---

## Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [uv](https://docs.astral.sh/uv/)

---

## Quick Start

**1. Clone and install dependencies:**
```bash
git clone <repo-url>
cd code-buster
uv sync --group dev
uv tool install .
```

**2. Run first-time setup** (creates `.buster` dir, starts Ollama, pulls the model, initialises the database):
```bash
buster setup
```

**3. Log your first incident:**
```bash
buster bust
```

**4. Recall a past solution:**
```bash
buster recall
```

---

## CLI Commands

| Command | Description |
|---|---|
| `buster setup` | First-time setup: creates `.buster`, starts Ollama, pulls model, initialises DB |
| `buster bust` | Log a new coding incident via AI agents, outputs a `.md` file |
| `buster save <file> [file2 ...]` | Save one or more bust `.md` files to the database |
| `buster save --all` | Save every `bust_*.md` file found in `.buster` |
| `buster recall` | Search past incidents and get an AI-narrated summary |
| `buster db` | Create the SQLite database in `.buster` (called automatically by `setup`) |
| `buster init` | Create the `.buster` directory and pull the Ollama model |

### `buster bust` — Log an incident

```
$ buster bust
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

Bust saved to: .buster/bust_20260530_142301_docker_daemon_not_running_in_devc.md
Review and edit it, then run: make save FILE=<path>
```

### `buster recall` — Search past incidents

```
$ buster recall
What problem are you facing right now?
> docker daemon won't connect inside my container

Searching your knowledge base... DONE!
Putting it into words... DONE!

You ran into the same issue with your devcontainer setup. Docker ps was
returning 'Cannot connect to the Docker daemon'. You tried mounting
/var/run/docker.sock from the host into the devcontainer, and that fixed it.
```

---

## Make Targets (development)

For day-to-day use (`bust`, `save`, `recall`) use the `buster` CLI directly — run `buster --help` to see all commands.
Make targets cover developer tooling and infrastructure that has no CLI equivalent.

| Command | Description |
|---|---|
| `make quick-start` | Sync deps, install CLI, run first-time setup |
| `make install` | Install the `buster` CLI tool locally |
| `make test` | Run the full test suite |
| `make lint` | Run ruff formatter and linter |
| `make pre-commit` | Run all pre-commit hooks |
| `make seed` | Seed the database with 32 example incidents |
| `make start-model` | Start the Ollama container and pull the model |
| `make stop-model` | Stop the Ollama container |
| `make down` | Stop all containers |
| `make clean` | Remove cache files and build artefacts |
| `make clean-buster` | Remove `.buster` and all stored data |
| `make full-clean` | Remove everything including `.venv` — use before a fresh `make quick-start` |

---

## Running Tests

```bash
make test
```

Tests that require Ollama are skipped automatically if the model is not running. The offline tests (DB, parsing, keywords, CLI) always run.

```
tests/
├── conftest.py        # shared fixtures
├── example_busts.py   # shared test data and ollama mark
├── test_bust.py       # bust creation pipeline
├── test_cli.py        # CLI command tests
├── test_database.py   # database layer tests
├── test_parse.py      # parse_md and extract_keywords unit tests
└── test_recall.py     # search and recall pipeline tests
```

---

## Implementation Challenges

**CrewAI config not packaged on install** — `@CrewBase` resolves YAML config paths relative to the installed package location. The `config/` directory was not included in the wheel because `pyproject.toml` had no `package-data` entry, causing `FileNotFoundError` at runtime. Fixed by adding `[tool.setuptools.package-data]` to include `*.yaml` files.

**CrewAI log bleed into the terminal** — CrewAI emits warnings and telemetry via Python's `logging` module. `contextlib.redirect_stderr` does not capture these because logging handlers hold a reference to the original `sys.stderr`. Fixed by calling `logging.disable(logging.WARNING)` before crew execution and restoring it in a `finally` block, alongside moving crew instantiation inside the suppression context.

**pytest module identity and DB patching** — `import database` (via `sys.path`) and `from db import database` (via the installed package) produce two separate module objects. Patching one with `monkeypatch.setattr` had no effect on the other, so `search_by_tags` was reading from the wrong `DB_PATH`. Fixed by aligning all test imports to use the package path (`from db import database`).

**Small model reliability** — `qwen2.5:1.5b` sometimes ignores conditional instructions (e.g. "if matches says no results, output this exact phrase"). Test assertions over LLM output phrasing were replaced with deterministic DB-layer checks, keeping only `result.raw.strip()` as the LLM guard.

---

## AI Usage

This project was built with assistance from **Claude Code (Anthropic)** throughout development. All generated code was reviewed and understood by the author before being committed.

| Area | How Claude Code was used |
|---|---|
| Architecture & design | Debating crew separation (Buster vs Recall as independent crews), agent role definitions, and the CLI↔AI interface contract |
| Bug investigation | Diagnosing CrewAI log bleed through `redirect_stderr`, the pytest module identity issue with `DB_PATH` patching, and the wrong empty-result string comparison in recall |
| Test suite design | Designing the test file structure, fixture strategy (deterministic hardcoded MDs vs Ollama-gated tests), and identifying edge cases — empty queries, stop-word-only inputs, missing files, idempotent setup |
| Optimisation debates | Discussing `DB_PATH` resolution timing (import-time vs call-time), tag search threshold behaviour, LLM output assertion strategy for a non-deterministic small model |
| CLI design | Structuring the `buster save` multi-file interface (`--all`, multiple args, partial failure handling) and the `buster setup` idempotent flow |
| Refactoring | Identifying duplicated logic (`visual_loading`, `extract_keywords`), dead code (`searcher` agent, vestigial `run()`), and missing package data configuration |
| Documentation | Scaffolding the architecture diagram, implementation challenges section, and this README |
