import httpx
import pytest


def _ollama_running() -> bool:
    try:
        httpx.get("http://localhost:11434", timeout=2)
        return True
    except Exception:
        return False


ollama = pytest.mark.skipif(not _ollama_running(), reason="Ollama not running")

BUSTS = [
    {
        "entry": (
            "Project: devcontainer setup. "
            "Issue: Docker daemon not running inside the devcontainer "
            "— docker ps returns 'Cannot connect to the Docker daemon'. "
            "Solution attempted: mounted /var/run/docker.sock from the "
            "host into the devcontainer. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: backend API. "
            "Issue: Git rebase conflict blocking the CI pipeline "
            "deployment. "
            "Solution attempted: resolved merge conflicts manually on the "
            "feature branch and rebased. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: database service. "
            "Issue: Database connection refused on application startup, "
            "psycopg2 raises OperationalError. "
            "Solution attempted: checked the connection string and "
            "environment variables for typos. "
            "Resolved?: no."
        ),
        "resolved": False,
    },
]

# Hardcoded MD files mirroring BUSTS — used by DB and recall tests without Ollama.
# Tags are chosen so recall queries match exactly the intended incident.
HARDCODED_MDS = [
    # Incident 0 — Docker daemon (targeted by direct + vague recall tests)
    (
        "# Docker Daemon Not Running in Devcontainer\n\n"
        "**Resolved:** yes\n\n"
        "## Problem\n"
        "Docker daemon not running inside the devcontainer. "
        "docker ps returns Cannot connect to the Docker daemon.\n\n"
        "## Solutions Tried\n"
        "- Mounted /var/run/docker.sock from the host into the devcontainer\n\n"
        "## Lesson\n"
        "Remember: Mount /var/run/docker.sock from the host.\n\n"
        "## Tags\n"
        "docker, daemon, devcontainer, socket\n"
    ),
    # Incident 1 — Git rebase (targeted by vague recall test)
    (
        "# Git Rebase Conflict Blocking CI Pipeline\n\n"
        "**Resolved:** yes\n\n"
        "## Problem\n"
        "Git rebase conflict blocking the CI pipeline deployment.\n\n"
        "## Solutions Tried\n"
        "- Resolved merge conflicts manually on the feature branch and rebased\n\n"
        "## Lesson\n"
        "Remember: Resolve merge conflicts manually before rebasing.\n\n"
        "## Tags\n"
        "git, rebase, conflict, ci, pipeline\n"
    ),
    # Incident 2 — DB connection (unresolved; not targeted by any recall test)
    (
        "# Database Connection Refused on Startup\n\n"
        "**Resolved:** no\n\n"
        "## Problem\n"
        "Database connection refused on application startup. "
        "psycopg2 raises OperationalError.\n\n"
        "## Solutions Tried\n"
        "- Checked the connection string and environment variables for typos\n\n"
        "## Lesson\n"
        "Remember: Check connection string and environment variables for typos.\n\n"
        "## Tags\n"
        "database, connection, psycopg2, postgresql, startup\n"
    ),
]
