import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "busts.db"

_STOP_WORDS = {
    "a", "an", "the", "is", "it", "my", "i", "am", "are", "was", "were",
    "have", "has", "had", "do", "does", "did", "in", "on", "at", "to", "for",
    "of", "and", "or", "but", "with", "not", "no", "by", "be", "been",
    "from", "as", "up", "out", "this", "that", "which", "who", "what",
    "how", "why", "when", "where", "can", "will", "would", "could", "should",
    "may", "might", "shall", "about", "into", "something", "getting", "keeps",
    "keep", "seems", "seem", "happening", "happen", "trying", "try", "using",
    "still", "just", "some", "also", "then", "than", "too", "very", "its",
}


def extract_keywords(text: str) -> list[str]:
    return [w for w in text.lower().split() if w not in _STOP_WORDS and len(w) > 2]


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
            if any(kw in tag.lower() or tag.lower() in kw for tag in tags)
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
    # Merge model-generated tags with keywords extracted from title and problem
    # so recall can find busts by the words users naturally type
    # Normalise model tags: split underscored compounds into individual words
    normalised = [w for tag in data["tags"] for w in tag.replace("_", " ").split()]
    extra = extract_keywords(f"{data['title']} {data['problem']}")
    merged_tags = list(dict.fromkeys(normalised + extra))  # dedup, preserve order
    params = {
        **data,
        "attempted_solutions": json.dumps(data["attempted_solutions"]),
        "tags": json.dumps(merged_tags),
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
