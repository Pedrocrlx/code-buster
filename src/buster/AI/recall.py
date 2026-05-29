#!/usr/bin/env python
import contextlib
import io
import sys
import threading
import time
from datetime import date

from buster.AI.crew import Recall
from db.database import search_by_tags

_STOP_WORDS = {
    "a",
    "an",
    "the",
    "is",
    "it",
    "my",
    "i",
    "am",
    "are",
    "was",
    "were",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "and",
    "or",
    "but",
    "with",
    "not",
    "no",
    "by",
    "be",
    "been",
    "from",
    "as",
    "up",
    "out",
    "this",
    "that",
    "which",
    "who",
    "what",
    "how",
    "why",
    "when",
    "where",
    "can",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "shall",
    "about",
    "into",
    "something",
    "getting",
    "keeps",
    "keep",
    "seems",
    "seem",
    "happening",
    "happen",
    "trying",
    "try",
    "using",
    "still",
    "just",
    "some",
    "also",
    "then",
    "than",
    "too",
    "very",
    "its",
}


def extract_keywords(query: str) -> list[str]:
    return [w for w in query.lower().split() if w not in _STOP_WORDS and len(w) > 2]


def filter_busts(query: str) -> str:
    keywords = extract_keywords(query)
    if not keywords:
        return "No relevant busts found."
    return search_by_tags(keywords)


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
    print("What problem are you facing right now?")
    query = input("> ").strip()

    matches = filter_busts(query)
    if matches == "No past busts found.":
        print("\nNo past busts in the knowledge base yet. Run `make bust` to add some!")
        return

    print()
    on_task_done, finish = visual_loading(
        [
            "Searching your knowledge base",
            "Putting it into words",
        ]
    )

    recall = Recall()
    recall._task_callback = on_task_done

    suppress_stdout = contextlib.redirect_stdout(io.StringIO())
    suppress_stderr = contextlib.redirect_stderr(io.StringIO())

    try:
        with suppress_stdout, suppress_stderr:
            result = recall.crew().kickoff(
                inputs={
                    "query": query,
                    "matches": matches,
                    "today": date.today().isoformat(),
                }
            )
    except Exception:
        finish()
        raise

    finish()
    print()
    print(result.raw)


if __name__ == "__main__":
    run()
