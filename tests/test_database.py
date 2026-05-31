import json
import sqlite3

from db.database import fetch_all_busts, init_db, save_bust
from save import parse_md


def test_create_sqlite_database(tmp_db):
    """init_db() creates a busts table with the expected schema."""
    init_db()

    with sqlite3.connect(tmp_db) as conn:
        cursor = conn.execute("PRAGMA table_info(busts)")
        columns = {row[1] for row in cursor.fetchall()}

    expected = {
        "id",
        "title",
        "problem",
        "attempted_solutions",
        "lesson",
        "tags",
        "resolved",
    }
    assert columns == expected


def test_save_bust_stores_tags_verbatim(tmp_db):
    """Tags are stored byte-for-byte as they appear in the .md file.
    No splitting, deduplication, or enrichment."""
    data = {
        "title": "Test bust",
        "problem": "Something broke.",
        "attempted_solutions": ["tried fixing it"],
        "lesson": "Remember: check it.",
        "tags": ["docker", "timeout", "docker"],  # duplicate intentional
        "resolved": True,
    }
    save_bust(data)

    with sqlite3.connect(tmp_db) as conn:
        (tags_json,) = conn.execute("SELECT tags FROM busts").fetchone()

    assert json.loads(tags_json) == ["docker", "timeout", "docker"]


def test_fetch_all_busts_empty_db(tmp_db):
    """fetch_all_busts returns the empty-state message when the DB has no rows."""
    init_db()
    assert fetch_all_busts() == "No past busts found."


def test_fetch_all_busts_format(tmp_db, hardcoded_md_files):
    """fetch_all_busts returns a formatted string covering all stored incidents,
    separated by --- between entries."""
    for md_file in hardcoded_md_files:
        save_bust(parse_md(md_file.read_text()))

    result = fetch_all_busts()

    assert "docker" in result.lower()
    assert "rebase" in result.lower() or "pipeline" in result.lower()
    assert "psycopg2" in result.lower() or "database" in result.lower()
    assert result.count("---") == 2  # 3 entries → 2 separators
