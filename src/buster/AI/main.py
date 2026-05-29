#!/usr/bin/env python
import contextlib
import io
import re
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from buster.AI.crew import Buster

BUSTS_DIR = Path.cwd() / ".buster"


def visual_loading(messages: list[str]):
    terminal = sys.stdout
    task_events = [threading.Event() for _ in messages]
    progress_done = threading.Event()

    def on_task_done(task_output):
        for task_event in task_events:
            if not task_event.is_set():
                task_event.set()
                break

    def visual_processing():
        spinning_wheel = "|/-\\"
        for message, task_event in zip(messages, task_events):
            terminal.write(f"{message}... ")
            terminal.flush()
            frame_index = 0
            while not task_event.is_set():
                terminal.write(spinning_wheel[frame_index % 4])
                terminal.flush()
                time.sleep(0.1)
                terminal.write("\b \b")
                terminal.flush()
                frame_index += 1
            terminal.write(" DONE!\n")
            terminal.flush()
        progress_done.set()

    def finish():
        for task_event in task_events:
            task_event.set()
        progress_done.wait(timeout=2)

    threading.Thread(target=visual_processing, daemon=True).start()
    return on_task_done, finish


def run(busts_dir: Path | None = None):
    if busts_dir is None:
        busts_dir = Path.cwd() / ".buster"

    print("What project were you working on?")
    project = input("> ").strip()

    print("\nWhat was the issue you were facing?")
    issue = input("> ").strip()

    print("\nWhat did you try to solve it?")
    solution = input("> ").strip()

    print("\nDid it work? (yes/no)")
    # saved as a boolean but asked in a yes/no format for better UX
    resolved = input("> ").strip().lower()

    entry = (  # How it's sent to the CrewAI, a single string with all the information
        # for better processing and understanding
        f"Project: {project}. "
        f"Issue: {issue}. "
        f"Solution(s) attempted: {solution}. "
        f"Resolved?: {resolved}."
    )

    print()
    on_task_done, finish = visual_loading(
        [
            "We are now processing your bust report",  # Task "Process"
            "We are now neatly organizing the information",  # Task "Organise"
        ]
    )

    buster = Buster()
    buster._task_callback = on_task_done

    # Stdout and stderr suppressed so CrewAI logs don't bleed into the terminal
    suppress_stdout = contextlib.redirect_stdout(
        io.StringIO()
    )  # Suppress standard output (logs, info, etc.)
    suppress_stderr = contextlib.redirect_stderr(
        io.StringIO()
    )  # Suppress standard error (errors, warnings, etc.)

    try:
        with suppress_stdout, suppress_stderr:
            result = buster.crew().kickoff(inputs={"entry": entry})
    except Exception:
        finish()
        raise

    finish()

    if result.pydantic is None:
        raise RuntimeError(
            "Failed to generate structured output. "
            "The AI model may be unreliable or offline."
        )

    data = result.pydantic.model_dump()
    data["resolved"] = resolved in ("yes", "y")

    busts_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "_", data["title"].lower()).strip("_")[:40]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = busts_dir / f"bust_{timestamp}_{slug}.md"

    resolved_str = "yes" if data["resolved"] else "no"
    solutions_md = "\n".join(f"- {s}" for s in data["attempted_solutions"])
    tags_str = ", ".join(data["tags"])

    md = (
        f"# {data['title']}\n\n"
        f"**Resolved:** {resolved_str}\n\n"
        f"## Problem\n{data['problem']}\n\n"
        f"## Solutions Tried\n{solutions_md}\n\n"
        f"## Lesson\n{data['lesson']}\n\n"
        f"## Tags\n{tags_str}\n"
    )

    filename.write_text(md)
    filepath = (
        filename.relative_to(Path.cwd())
        if filename.is_relative_to(Path.cwd())
        else filename
    )
    print(f"\nBust saved to: {filepath}")
    print("Review and edit it, then run: make save FILE=<path>")


if __name__ == "__main__":
    run()
