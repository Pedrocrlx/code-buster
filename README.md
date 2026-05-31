# Code Buster

A local-first CLI tool for developers to log coding busts and recall past solutions — powered by AI agents running fully offline via Ollama. No data leaves your machine.

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
│  → BustEntry       │     │  → prose narration  │
│    (Pydantic)      │     │                     │
└─────────┬──────────┘     └──────────┬──────────┘
          │                            │
     word_filter.md                    │
     (tag middleware)                  │
          │        ┌───────────────────┘
          ▼        ▼
┌──────────────────────────────────────────────────────┐
│                 Data Layer  (SQLite)                  │
│  save_bust · fetch_all_busts · search_by_tags        │
└──────────────────────────────────────────────────────┘
```

**Bust flow** — the developer describes a bust at the CLI. The Buster crew runs two agents in sequence: `processor` extracts the problem and solutions from free text; `organizer` structures them into a validated Pydantic model. Before writing to disk, `word_filter.md` strips noise words from the AI-generated tags. The result is written as a `.md` file for the developer to review and edit, then saved to SQLite verbatim via `buster save`.

**Recall flow** — the developer describes a current problem. The query is split into keywords and matched against stored bust tags. Matching busts are passed to the Recall crew's `narrator` agent, which produces a short conversational summary of what happened before and what worked.

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

**2. Run first-time setup** (creates `.busts` dir, starts Ollama, pulls the model, initialises the database):
```bash
buster setup
```

**3. Log your first bust:**
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
| `buster setup` | First-time setup: creates `.busts`, starts Ollama, pulls model, initialises DB |
| `buster bust` | Log a new bust via AI agents, outputs a `.md` file for review |
| `buster save <file> [file2 ...]` | Save one or more bust `.md` files to the database |
| `buster save --all` | Save every `bust_*.md` file found in `.busts` |
| `buster recall` | Search past busts and get an AI-narrated summary |
| `buster db` | Create the SQLite database in `.busts` (called automatically by `setup`) |
| `buster init` | Create the `.busts` directory and pull the Ollama model |

### `buster bust` — Log a bust

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

Bust saved to: .busts/bust_1748702581.md
Review and edit it, then run: buster save <path>
```

### `buster recall` — Search past busts

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
| `make seed` | Write 32 example bust `.md` files to `.busts/` for review |
| `make start-model` | Start the Ollama container and pull the model |
| `make stop-model` | Stop the Ollama container |
| `make down` | Stop all containers |
| `make clean` | Remove cache files and build artefacts |
| `make clean-buster` | Remove `.busts` and all stored data |
| `make full-clean` | Remove everything including `.venv` — use before a fresh `make quick-start` |

---

## Running Tests

```bash
make test
```

Tests that require Ollama are skipped automatically if the model is not running. The offline tests (DB, parsing, CLI) always run.

```
tests/
├── conftest.py              # shared fixtures
├── example_busts.py         # loads fixture files, exposes HARDCODED_MDS / AI_ENTRY / ollama mark
├── fixtures/
│   ├── resolved.md          # hardcoded resolved bust (Docker daemon)
│   ├── unresolved.md        # hardcoded unresolved bust (DB connection)
│   └── pending_processing.md  # raw entry string fed to the AI crew in Ollama tests
├── test_bust.py             # bust creation pipeline and word filter middleware
├── test_cli.py              # CLI command tests
├── test_database.py         # database layer tests
├── test_parse.py            # parse_md unit tests
└── test_recall.py           # search and recall pipeline tests
```

---

## Implementation Challenges

**Makefile vs CLI boundary** — The project has both a `Makefile` for developer tooling and a `buster` CLI for end-user commands. Early on the boundary was unclear, with some operations duplicated across both. The split was resolved by treating the CLI as the user-facing interface for all runtime operations (`bust`, `save`, `recall`, `setup`) and the Makefile strictly as a dev convenience layer for things with no CLI equivalent — running tests, linting, seeding data, managing containers.

**Keyword-based recall limitation** — The recall system matches a user's query against stored bust tags by splitting the query into keywords and checking for overlap. This works for direct matches but struggles with synonyms, related concepts, or queries phrased differently from how the tags were generated. A semantic search approach (e.g. embedding similarity) would be more robust but was out of scope given the offline-first constraint and the model size available via Ollama.

**Small model reliability** — `qwen2.5:1.5b` sometimes ignores conditional instructions (e.g. "if matches says no results, output this exact phrase"). Test assertions over LLM output phrasing were replaced with deterministic DB-layer checks, keeping only `result.raw.strip()` as the LLM guard.

---

## AI Usage

This project was built with assistance from **Claude Code (Anthropic)** throughout development. Claude Code was involved in most phases of development — from initial planning through to final refactoring. It was used as a thinking partner as much as a code generator, and all output was reviewed and understood before being accepted.

| Area | How Claude Code was used |
|---|---|
| Design | Thinking through how to split responsibilities across agents and layers, and where to draw the line between what belongs in the AI crew vs. the CLI |
| Framework research | Understanding how third-party libraries behave internally — e.g. why CrewAI logs couldn't be silenced with standard stream redirection, or how package data needs to be declared to survive installation |
| Debugging | Investigating bugs where the root cause wasn't obvious — patching the wrong module object, a string comparison that never matched, telemetry output polluting the terminal |
| Test strategy | Deciding what's worth testing, how to structure fixtures, and how to keep slow AI-dependent tests separate from fast deterministic ones |
| Trade-off discussions | Talking through small decisions like schema columns, file naming, search thresholds, and when not to abstract |
| Refactoring | Identifying dead code, duplication, and structural issues; discussing what to simplify vs. what to leave alone |
| Compliance | Cross-checking the project against assignment requirements and spotting missing deliverables (e.g. git tag, CI coverage) |
| Planning | Breaking the project into epics and tasks, and helping split work across team members in a way that minimised overlap and dependency conflicts |
| Writing | Improving phrasing and tone throughout — commit messages, documentation, and challenge descriptions — to be clear and professional without losing the original meaning |
| Documentation | Drafting the architecture diagram, the implementation challenges section, and this README |
