#!/usr/bin/env python
import contextlib
import io
import sys
import threading
import time
from crew import Buster
from database import save_bust


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


def run():
    print("What project were you working on?")  # Saved like an email subject
    project = input("> ").strip()

    print("\nWhat was the issue you were facing?")  # Description of the problem
    issue = input("> ").strip()

    print(
        "\nWhat did you try to solve it?"
    )  # The solution or solutions attempted, can be multiple and separated by commas
    solution = input("> ").strip()

    print("\nDid it work? (yes/no)")  # Whether the issue was resolved or not,
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

    data = result.pydantic.model_dump()

    data["resolved"] = resolved in ("yes", "y")

    bust_id = save_bust(data)
    print(f"Eveything Processed & Bust Saved! (Bust #{bust_id})")
