#!/usr/bin/env python
import contextlib
import io
import json
import sys
import threading
import time
import warnings
from datetime import datetime
from pathlib import Path

from buster.crew import Buster

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

_MESSAGES = [
    "Processing your incident",
    "Organising your report",
]


def run():
    project  = input("What project were you working on?\n> ").strip()
    issue    = input("\nWhat was the issue?\n> ").strip()
    solution = input("\nWhat did you do to solve it?\n> ").strip()
    resolved = input("\nWas it solved? (yes/no)\n> ").strip().lower()

    entry = (
        f"Project: {project}. "
        f"Issue: {issue}. "
        f"Solution attempted: {solution}. "
        f"Resolved: {resolved}."
    )

    slug = project.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    filename = Path("output") / f"{slug}_{timestamp}.json"

    terminal = sys.stdout
    spinner_frames = "|/-\\"
    task_events = [threading.Event() for _ in _MESSAGES]
    progress_done = threading.Event()

    def on_task_done(_):
        for task_event in task_events:
            if not task_event.is_set():
                task_event.set()
                break

    def show_progress():
        for message, task_event in zip(_MESSAGES, task_events):
            terminal.write(f"{message}... ")
            terminal.flush()
            frame_index = 0
            while not task_event.is_set():
                terminal.write(spinner_frames[frame_index % 4])
                terminal.flush()
                time.sleep(0.1)
                terminal.write("\b \b")
                terminal.flush()
                frame_index += 1
            terminal.write("✓\n")
            terminal.flush()
        progress_done.set()

    threading.Thread(target=show_progress, daemon=True).start()

    buster = Buster()
    buster._task_callback = on_task_done

    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = buster.crew().kickoff(inputs={"entry": entry})
    except Exception as e:
        for task_event in task_events:
            task_event.set()
        progress_done.wait(timeout=2)
        raise Exception(f"An error occurred while running the crew: {e}")

    for task_event in task_events:
        task_event.set()
    progress_done.wait(timeout=2)

    data = result.pydantic.model_dump()
    data["resolved"] = resolved in ("yes", "y")

    Path("output").mkdir(exist_ok=True)
    filename.write_text(json.dumps(data, indent=2))
    print(f"Report saved to {filename}")
