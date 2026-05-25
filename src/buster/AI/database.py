import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "busts.db"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS busts (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                title               TEXT NOT NULL,
                problem             TEXT NOT NULL,
                attempted_solutions TEXT NOT NULL,
                lesson              TEXT NOT NULL,
                tags                TEXT NOT NULL,
                resolved            INTEGER NOT NULL,
                created_at          TEXT NOT NULL
            )
        """)


def fetch_all_busts() -> str:
    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM busts ORDER BY created_at DESC"
        ).fetchall()
    if not rows:
        return "No past incidents found."
    parts = []
    for row in rows:
        solutions = ", ".join(json.loads(row["attempted_solutions"]))
        tags = ", ".join(json.loads(row["tags"]))
        resolved = "yes" if row["resolved"] else "no"
        parts.append(
            f"#{row['id']} — {row['title']}\n"
            f"Date: {row['created_at']}\n"
            f"Problem: {row['problem']}\n"
            f"Solutions tried: {solutions}\n"
            f"Lesson: {row['lesson']}\n"
            f"Tags: {tags}\n"
            f"Resolved: {resolved}"
        )
    return "\n---\n".join(parts)


RECALL_MIN_KEYWORD_MATCHES = 2  # minimum keyword hits required to surface a bust


def search_by_tags(keywords: list[str]) -> str:
    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM busts ORDER BY created_at DESC"
        ).fetchall()
    if not rows:
        return "No past busts found."
    threshold = max(1, min(RECALL_MIN_KEYWORD_MATCHES, len(keywords)))
    matches = []
    for row in rows:
        tags = json.loads(row["tags"])
        hits = sum(
            1 for kw in keywords
            if any(kw in tag or tag in kw for tag in tags)
        )
        if hits >= threshold:
            solutions = ", ".join(json.loads(row["attempted_solutions"]))
            matches.append(
                f"#{row['id']} — {row['title']}\n"
                f"Date: {row['created_at']}\n"
                f"Problem: {row['problem']}\n"
                f"Solutions tried: {solutions}\n"
                f"Lesson: {row['lesson']}\n"
                f"Tags: {', '.join(tags)}\n"
                f"Resolved: {'yes' if row['resolved'] else 'no'}"
            )
    return "\n---\n".join(matches) if matches else "No relevant busts found."


def save_bust(data: dict) -> int:
    init_db()
    params = {
        **data,
        "attempted_solutions": json.dumps(data["attempted_solutions"]),
        "tags": json.dumps(data["tags"]),
        "resolved": int(data["resolved"]),
        "created_at": datetime.now().isoformat(),
    }
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            """INSERT INTO busts (title, problem, attempted_solutions,
            lesson, tags, resolved, created_at)
               VALUES (:title, :problem, :attempted_solutions, :lesson,
            :tags, :resolved, :created_at)""",
            params,
        )
        return cursor.lastrowid
