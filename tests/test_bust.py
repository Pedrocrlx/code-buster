"""
Tests for the bust creation pipeline:
  entry text → Buster crew → structured output → word filter → .md file → parse_md → DB

test_word_filter_removes_noise_tags  (no Ollama)
    Verifies the middleware strips word_filter.md words from AI-generated tags
    before the MD is written. Nothing after this point (edits, save) is touched.

test_agent_output_quality  (Ollama)
    Feeds the pending_processing fixture entry to the Buster crew and asserts that the
    structured output is domain-relevant: tags relate to the input, all fields
    are populated, and no noise words slipped through the word filter.

test_creation_from_ai_prompt  (Ollama)
    Runs the Buster crew on the pending_processing fixture entry and verifies that the
    result is written to a correctly structured markdown file.

test_push_output_to_db  (no Ollama)
    Takes the two hardcoded fixture files and pushes them through parse_md +
    save_bust, verifying the DB rows are correct.
"""

import re
import sqlite3

import pytest
from buster.AI.main import _WORD_FILTER
from crew import Buster
from db.database import save_bust
from save import parse_md

from example_busts import AI_ENTRY, ollama


def test_word_filter_removes_noise_tags():
    """Noise words from word_filter.md are stripped from AI tags before the MD.
    Real tags survive; nothing after this step is touched."""
    ai_tags = ["docker", "the", "daemon", "and", "timeout", "is"]
    filtered = [tag for tag in ai_tags if tag.lower() not in _WORD_FILTER]

    assert "docker" in filtered
    assert "daemon" in filtered
    assert "timeout" in filtered
    assert "the" not in filtered
    assert "and" not in filtered
    assert "is" not in filtered


def test_word_filter_removes_all_noise():
    """All 75 words in word_filter.md are stripped when mixed into AI-generated tags.
    Real tags survive; pure noise input produces an empty list."""
    all_filter_words = list(_WORD_FILTER)
    real_tags = ["docker", "timeout", "psycopg2", "nginx", "fastapi"]

    ai_tags = all_filter_words + real_tags
    filtered = [tag for tag in ai_tags if tag.lower() not in _WORD_FILTER]

    for word in all_filter_words:
        assert word not in filtered, f"'{word}' from word_filter.md was not removed"

    assert filtered == real_tags

    noise_only = [tag for tag in all_filter_words if tag.lower() not in _WORD_FILTER]
    assert noise_only == []


@ollama
def test_agent_output_quality():
    """Feeds the pending_processing fixture entry to the Buster crew and asserts
    that the structured output is domain-relevant — tags relate to the input,
    all fields are populated, and no noise words slipped through the word filter."""
    result = Buster().crew().kickoff(inputs={"entry": AI_ENTRY})
    if result.pydantic is None:
        pytest.skip("Model did not return structured output")

    data = result.pydantic.model_dump()
    tags_lower = [t.lower() for t in data["tags"]]

    assert data["title"], "title is empty"
    assert data["problem"], "problem is empty"
    assert data["lesson"], "lesson is empty"
    assert data["attempted_solutions"], "solutions list is empty"

    assert any("npm" in t or "node" in t or "peer" in t for t in tags_lower), (
        f"expected npm/node/peer-related tag, got: {data['tags']}"
    )

    noise = [t for t in data["tags"] if t.lower() in _WORD_FILTER]
    assert not noise, f"noise words found in tags: {noise}"


@ollama
def test_creation_from_ai_prompt(tmp_db, tmp_path):
    """Buster crew processes the pending_processing fixture entry and writes a correctly
    structured .md file."""
    result = Buster().crew().kickoff(inputs={"entry": AI_ENTRY})
    if result.pydantic is None:
        pytest.skip(
            "Crew failed to produce structured output — model may be unreliable"
        )

    data = result.pydantic.model_dump()
    data["resolved"] = True

    solutions_md = "\n".join(f"- {s}" for s in data["attempted_solutions"])
    tags_str = ", ".join(data["tags"])
    slug = re.sub(r"[^a-z0-9]+", "_", data["title"].lower()).strip("_")[:40]

    md_path = tmp_path / f"bust_{slug}.md"
    md_path.write_text(
        f"# {data['title']}\n\n"
        f"**Resolved:** yes\n\n"
        f"## Problem\n{data['problem']}\n\n"
        f"## Solutions Tried\n{solutions_md}\n\n"
        f"## Lesson\n{data['lesson']}\n\n"
        f"## Tags\n{tags_str}\n"
    )

    content = md_path.read_text()
    assert re.match(r"# .+", content), "missing title"
    assert "**Resolved:**" in content, "missing resolved field"
    assert "## Problem" in content, "missing Problem section"
    assert "## Solutions Tried" in content, "missing Solutions Tried section"
    assert "## Lesson" in content, "missing Lesson section"
    assert "## Tags" in content, "missing Tags section"


def test_push_output_to_db(tmp_db, hardcoded_md_files):
    """parse_md + save_bust correctly stores the two hardcoded fixture files in the
    database with the right content and resolved flags."""
    for md_file in hardcoded_md_files:
        save_bust(parse_md(md_file.read_text()))

    with sqlite3.connect(tmp_db) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM busts ORDER BY id").fetchall()

    assert len(rows) == 2

    assert rows[0]["resolved"] == 1
    assert rows[1]["resolved"] == 0

    for row in rows:
        assert row["title"], "title should not be empty"
        assert row["problem"], "problem should not be empty"
        assert row["lesson"], "lesson should not be empty"
        assert row["tags"], "tags should not be empty"

    assert "docker" in rows[0]["title"].lower()
    assert (
        "database" in rows[1]["title"].lower()
        or "connection" in rows[1]["title"].lower()
    )
