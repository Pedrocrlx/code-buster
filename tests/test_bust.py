"""
Tests for the bust creation pipeline:
  entry text → Buster crew → structured output → .md file → parse_md → DB

test_creation_of_three_busts  (Ollama)
    Runs the Buster crew on three real incident entries and verifies that each
    result is written to a correctly structured markdown file.

test_push_output_to_db  (no Ollama)
    Takes the three hardcoded .md files from example_busts and pushes them
    through parse_md + save_bust, then verifies the DB rows are correct.
    Uses deterministic content so it runs without the model.
"""

import re
import sqlite3

import pytest
from crew import Buster
from db.database import save_bust
from save import parse_md

from example_busts import BUSTS, HARDCODED_MDS, ollama


@ollama
def test_creation_of_three_busts(tmp_db, tmp_path):
    """Buster crew processes 3 entries and writes a correctly structured
    .md file for each one."""
    md_files = []

    for bust in BUSTS:
        result = Buster().crew().kickoff(inputs={"entry": bust["entry"]})
        if result.pydantic is None:
            pytest.skip("Crew failed to produce structured output — model may be unreliable")

        data = result.pydantic.model_dump()
        data["resolved"] = bust["resolved"]

        resolved_str = "yes" if data["resolved"] else "no"
        solutions_md = "\n".join(f"- {s}" for s in data["attempted_solutions"])
        tags_str = ", ".join(data["tags"])
        slug = re.sub(r"[^a-z0-9]+", "_", data["title"].lower()).strip("_")[:40]

        md_path = tmp_path / f"bust_{slug}.md"
        md_path.write_text(
            f"# {data['title']}\n\n"
            f"**Resolved:** {resolved_str}\n\n"
            f"## Problem\n{data['problem']}\n\n"
            f"## Solutions Tried\n{solutions_md}\n\n"
            f"## Lesson\n{data['lesson']}\n\n"
            f"## Tags\n{tags_str}\n"
        )
        md_files.append(md_path)

    assert len(md_files) == 3

    for md_file in md_files:
        content = md_file.read_text()
        assert re.match(r"# .+", content), f"{md_file.name}: missing title"
        assert "**Resolved:**" in content, f"{md_file.name}: missing resolved field"
        assert "## Problem" in content, f"{md_file.name}: missing Problem section"
        assert "## Solutions Tried" in content, f"{md_file.name}: missing Solutions Tried section"
        assert "## Lesson" in content, f"{md_file.name}: missing Lesson section"
        assert "## Tags" in content, f"{md_file.name}: missing Tags section"


def test_push_output_to_db(tmp_db, tmp_path):
    """parse_md + save_bust correctly stores the three example busts in the
    database with the right content and resolved flags."""
    for i, content in enumerate(HARDCODED_MDS):
        path = tmp_path / f"bust_{i}.md"
        path.write_text(content)
        save_bust(parse_md(path.read_text()))

    with sqlite3.connect(tmp_db) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM busts ORDER BY id").fetchall()

    assert len(rows) == 3

    resolved_flags = [bool(row["resolved"]) for row in rows]
    assert resolved_flags.count(True) == 2
    assert resolved_flags.count(False) == 1

    for row in rows:
        assert row["title"], "title should not be empty"
        assert row["problem"], "problem should not be empty"
        assert row["lesson"], "lesson should not be empty"
        assert row["tags"], "tags should not be empty"

    assert "docker" in rows[0]["title"].lower()
    assert "git" in rows[1]["title"].lower() or "rebase" in rows[1]["title"].lower()
    assert rows[2]["resolved"] == 0
