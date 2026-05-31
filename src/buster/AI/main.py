import contextlib
import io
import logging
import time
from pathlib import Path

from buster.AI.crew import Buster
from buster.AI.ui import visual_loading
from settings import BUSTS_DIR_NAME, BUST_PREFIX

BUSTS_DIR = Path.cwd() / BUSTS_DIR_NAME

# loaded once at startup — filters noise words from AI-generated tags
# edit word_filter.md to add or remove words (one per line, # for comments)
_WORD_FILTER = {
    line.strip()
    for line in (Path(__file__).parent / "word_filter.md").read_text().splitlines()
    if line.strip() and not line.startswith("#")
}


# 'Questionarie' for the user to fill about their bust
# Outputs to an md file, for user review and possible editing
def run(busts_dir: Path | None = None):
    if busts_dir is None:
        busts_dir = Path.cwd() / BUSTS_DIR_NAME

    print("What project were you working on?")
    project = input("> ").strip()
    if not project:
        raise ValueError("Project name cannot be empty.")

    print("\nWhat was the issue you were facing?")
    issue = input("> ").strip()
    if not issue:
        raise ValueError("Issue description cannot be empty.")

    print("\nWhat did you try to solve it?")
    solution = input("> ").strip()
    if not solution:
        raise ValueError("Solution description cannot be empty.")

    print("\nDid it work? (yes/no)")
    resolved = input("> ").strip().lower()

    # Model will use template to parse the user's input and generate a bust entry
    entry = (
        f"Project: {project}. "
        f"Issue: {issue}. "
        f"Solution(s) attempted: {solution}. "
        f"Resolved?: {resolved}."
    )

    print()
    on_task_done, finish = visual_loading(
        [
            # Shows during 'process' task:
            "We are now processing your bust report",
            # Shows during 'organize' task:
            "We are now neatly organizing the information",
        ]
    )

    suppress_stdout = contextlib.redirect_stdout(io.StringIO())
    suppress_stderr = contextlib.redirect_stderr(io.StringIO())

    try:
        logging.disable(logging.WARNING)
        with suppress_stdout, suppress_stderr:
            buster = Buster()
            buster._task_callback = on_task_done
            result = buster.crew().kickoff(inputs={"entry": entry})
    except Exception:
        finish()
        raise
    finally:
        logging.disable(logging.NOTSET)

    finish()

    # If model fails generation, skips saving and raises an error
    if result.pydantic is None:
        raise RuntimeError(
            "Failed to generate structured output. "
            "The AI model may be unreliable or offline."
        )

    data = result.pydantic.model_dump()
    # Booleans as true when input is "yes" or "y", false otherwise
    # Edit to accept other inputs as true
    data["resolved"] = resolved in ("yes", "y")

    # middleware: strip noise words from AI-generated tags before writing to MD
    # anything after this point (user edits, save to DB) is untouched
    data["tags"] = [tag for tag in data["tags"] if tag.lower() not in _WORD_FILTER]

    busts_dir.mkdir(parents=True, exist_ok=True)
    filename = busts_dir / f"{BUST_PREFIX}{int(time.time())}.md"

    resolved_str = "yes" if data["resolved"] else "no"
    solutions_md = "\n".join(f"- {s}" for s in data["attempted_solutions"])
    tags_str = ", ".join(data["tags"])

    # Formats the structured data into markdown for user review and possible editing
    md = (
        f"# {data['title']}\n\n"
        f"**Resolved:** {resolved_str}\n\n"
        f"## Problem\n{data['problem']}\n\n"
        f"## Solutions Tried\n{solutions_md}\n\n"
        f"## Lesson\n{data['lesson']}\n\n"
        f"## Tags\n{tags_str}\n"
    )

    # Saves said markdown to a file, and prints path for user review
    filename.write_text(md)
    filepath = (
        filename.relative_to(Path.cwd())
        if filename.is_relative_to(Path.cwd())
        else filename
    )
    print(f"\nBust saved to: {filepath}")
    print("Review and edit it, then run: buster save <path>")


if __name__ == "__main__":
    run()
