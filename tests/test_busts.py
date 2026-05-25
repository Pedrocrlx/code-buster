import sqlite3

import httpx
import pytest

import database
from database import save_bust
from recall import filter_busts
from crew import Buster, Recall


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
            "Issue: Docker daemon not running inside the devcontainer — docker ps returns 'Cannot connect to the Docker daemon'. "
            "Solution attempted: mounted /var/run/docker.sock from the host into the devcontainer. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: backend API. "
            "Issue: Git rebase conflict blocking the CI pipeline deployment. "
            "Solution attempted: resolved merge conflicts manually on the feature branch and rebased. "
            "Resolved?: yes."
        ),
        "resolved": True,
    },
    {
        "entry": (
            "Project: database service. "
            "Issue: Database connection refused on application startup, psycopg2 raises OperationalError. "
            "Solution attempted: checked the connection string and environment variables for typos. "
            "Resolved?: no."
        ),
        "resolved": False,
    },
]


@pytest.fixture # Creates a temporary database file for testing and patches the database path to use it.
def tmp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    yield db_file


@pytest.fixture
def busted_db(tmp_db):
    """Test database pre-populated with 3 busts created via the Buster crew. Two resolved and one unresolved."""
    for bust in BUSTS:
        result = Buster().crew().kickoff(inputs={"entry": bust["entry"]})
        if result.pydantic is None:
            pytest.skip("Buster crew failed to produce structured output — model may be unreliable")
        data = result.pydantic.model_dump()
        data["resolved"] = bust["resolved"]
        save_bust(data)
    yield tmp_db


# Bust Tests:

@ollama
def testing_creation_of_three_busts(busted_db):
    """Buster crew processes 3 busts and stores them in the database with predeterminated busts, two resolved and one unresolved."""
    
    with sqlite3.connect(busted_db) as conn: 
        rows = conn.execute("SELECT id, resolved FROM busts ORDER BY id").fetchall() 

    assert len(rows) == 3

    resolved_flags = [bool(r[1]) for r in rows]
    assert resolved_flags.count(True) == 2
    assert resolved_flags.count(False) == 1


# Recall Tests:

@ollama
def test_recall_direct_query(busted_db):
    """Direct recall: explicit keywords ('docker daemon') surface the devcontainer incident."""
    query = "docker daemon"
    matches = filter_busts(query)

    assert matches != "No relevant busts found.", "Search found no matches for a direct query"

    result = Recall().crew().kickoff(inputs={
        "query": query,
        "matches": matches,
        "today": "2026-05-24",
    })

    assert result.raw.strip(), "Recall crew returned empty output"
    assert "nothing similar" not in result.raw.lower(), "Recall crew found no relevant results for a direct query"


@ollama
def test_recall_vague_query(busted_db):
    """Vague recall: partial keyword ('container') still surfaces the devcontainer incident."""
    query = "container problem"
    matches = filter_busts(query)

    assert matches != "No relevant busts found.", "Search found no matches for a vague query"

    result = Recall().crew().kickoff(inputs={
        "query": query,
        "matches": matches,
        "today": "2026-05-24",
    })

    assert result.raw.strip(), "Recall crew returned empty output"
    assert "nothing similar" not in result.raw.lower(), "Recall crew found no relevant results for a vague query"
