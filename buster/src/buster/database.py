import json
import sqlite3
from datetime import datetime
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


def save_bust(data: dict) -> int:
    init_db()
    params = {
        **data,
        "attempted_solutions": json.dumps(data["attempted_solutions"]),
        "tags":                json.dumps(data["tags"]),
        "resolved":            int(data["resolved"]),
        "created_at":          datetime.now().isoformat(),
    }
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            """INSERT INTO busts (title, problem, attempted_solutions, lesson, tags, resolved, created_at)
               VALUES (:title, :problem, :attempted_solutions, :lesson, :tags, :resolved, :created_at)""",
            params
        )
        return cursor.lastrowid
