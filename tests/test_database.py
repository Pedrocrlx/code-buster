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
        "id", "title", "problem", "attempted_solutions",
        "lesson", "tags", "resolved", "created_at",
    }
    assert columns == expected


def test_stop_words_absent_from_tags(tmp_db, hardcoded_md_files):
    """Tags stored in the DB after save_bust contain no stop words."""
    from db.database import _STOP_WORDS

    for md_file in hardcoded_md_files:
        save_bust(parse_md(md_file.read_text()))

    with sqlite3.connect(tmp_db) as conn:
        rows = conn.execute("SELECT tags FROM busts").fetchall()

    for (tags_json,) in rows:
        tags = json.loads(tags_json)
        stop_words_found = [t for t in tags if t in _STOP_WORDS]
        assert not stop_words_found, (
            f"Stop words found in stored tags: {stop_words_found}"
        )


def test_save_bust_normalises_underscored_tags(tmp_db):
    """Underscored compound tags are split into individual words by save_bust."""
    data = {
        "title": "Test incident",
        "problem": "Something broke.",
        "attempted_solutions": ["tried fixing it"],
        "lesson": "Remember: check it.",
        "tags": ["docker_daemon", "ci_pipeline"],
        "resolved": True,
    }
    save_bust(data)

    with sqlite3.connect(tmp_db) as conn:
        (tags_json,) = conn.execute("SELECT tags FROM busts").fetchone()

    tags = json.loads(tags_json)
    assert "docker" in tags
    assert "daemon" in tags
    assert "ci" in tags
    assert "pipeline" in tags
    assert "docker_daemon" not in tags


def test_fetch_all_busts_empty_db(tmp_db):
    """fetch_all_busts returns the empty-state message when the DB has no rows."""
    init_db()
    assert fetch_all_busts() == "No past incidents found."


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
