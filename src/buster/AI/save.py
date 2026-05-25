#!/usr/bin/env python
import re
import sys
from pathlib import Path
from database import save_bust


def parse_md(text: str) -> dict:
    def section(name: str) -> str:
        match = re.search(rf"## {name}\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
        return match.group(1).strip() if match else ""

    title_match = re.match(r"# (.+)", text)
    title = title_match.group(1).strip() if title_match else ""

    resolved_match = re.search(r"\*\*Resolved:\*\*\s*(\w+)", text)
    resolved_str = resolved_match.group(1).lower() if resolved_match else "no"

    solutions_block = section("Solutions Tried")
    solutions = [line.lstrip("- ").strip() for line in solutions_block.splitlines() if line.strip()]

    tags_block = section("Tags")
    tags = [t.strip() for t in tags_block.split(",") if t.strip()]

    return {
        "title": title,
        "problem": section("Problem"),
        "attempted_solutions": solutions,
        "lesson": section("Lesson"),
        "tags": tags,
        "resolved": resolved_str in ("yes", "y"),
    }


def run():
    if len(sys.argv) < 2:
        print("Usage: uv run save.py <path-to-bust-file.md>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    data = parse_md(path.read_text())

    if not data["title"]:
        print("Could not parse title from file. Make sure it starts with '# Title'.")
        sys.exit(1)

    bust_id = save_bust(data)
    print(f"Bust #{bust_id} saved to database.")


if __name__ == "__main__":
    run()
