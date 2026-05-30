import re


def parse_md(text: str) -> dict:
    def section(name: str) -> str:
        match = re.search(rf"## {name}\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
        return match.group(1).strip() if match else ""

    title_match = re.match(r"# (.+)", text)
    title = title_match.group(1).strip() if title_match else ""

    resolved_match = re.search(r"\*\*Resolved:\*\*\s*(\w+)", text)
    resolved_str = resolved_match.group(1).lower() if resolved_match else "no"

    # Section names below must match the ## headings written by main.py.
    # If you rename a section in one place, rename it in both.
    solutions_block = section("Solutions Tried")
    solutions = [
        line.lstrip("- ").strip()
        for line in solutions_block.splitlines()
        if line.strip()
    ]

    tags_block = section("Tags")
    tags = [t.strip() for t in tags_block.split(",") if t.strip()]

    return {
        "title": title,
        "problem": section("Problem"),
        "attempted_solutions": solutions,
        "lesson": section("Lesson"),
        "tags": tags,
        # Change accepted values here to match whatever main.py writes for resolved
        "resolved": resolved_str in ("yes", "y"),
    }
