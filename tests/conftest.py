import pytest
from db import database
from db.database import save_bust
from save import parse_md

from example_busts import HARDCODED_MDS


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    yield db_file


@pytest.fixture
def hardcoded_md_files(tmp_path):
    """Three pre-written MD files — no Ollama needed."""
    files = []
    for i, content in enumerate(HARDCODED_MDS):
        path = tmp_path / f"bust_{i}.md"
        path.write_text(content)
        files.append(path)
    return files


@pytest.fixture
def busted_db(tmp_db, hardcoded_md_files):
    """DB pre-populated from the hardcoded MDs via parse_md + save_bust.
    No Ollama needed — the DB content is fully deterministic."""
    for md_file in hardcoded_md_files:
        save_bust(parse_md(md_file.read_text()))
    yield tmp_db
