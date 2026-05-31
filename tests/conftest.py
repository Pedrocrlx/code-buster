from pathlib import Path

import pytest
from db import database
from db.database import save_bust
from save import parse_md

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    yield db_file


@pytest.fixture
def hardcoded_md_files():
    """The two pre-written fixture files — no Ollama needed."""
    return [
        FIXTURES_DIR / "resolved.md",
        FIXTURES_DIR / "unresolved.md",
    ]


@pytest.fixture
def busted_db(tmp_db, hardcoded_md_files):
    """DB pre-populated from the hardcoded fixtures via parse_md + save_bust.
    No Ollama needed — the DB content is fully deterministic."""
    for md_file in hardcoded_md_files:
        save_bust(parse_md(md_file.read_text()))
    yield tmp_db
