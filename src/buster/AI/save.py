import re


# Parses the markdown file back into a dict to save it to DB
def parse_md(text: str) -> dict:
    def section(name: str) -> str:
        match = re.search(rf"## {name}\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
        return match.group(1).strip() if match else ""

    title_match = re.match(r"# (.+)", text)
    title = title_match.group(1).strip() if title_match else ""

    resolved_match = re.search(r"\*\*Resolved:\*\*\s*(\w+)", text)
    resolved_str = resolved_match.group(1).lower() if resolved_match else "no"

    # Extracts solutions from 'Solutions Tried', breaking them into a list
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
        "resolved": resolved_str in ("yes", "y"),
    }
