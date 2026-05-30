#!/usr/bin/env python
import contextlib
import io
import logging
from datetime import date

from buster.AI.crew import Recall
from buster.AI.ui import visual_loading
from db.database import extract_keywords, search_by_tags


def filter_busts(query: str) -> str:
    keywords = extract_keywords(query)
    if not keywords:
        return "No relevant busts found."
    return search_by_tags(keywords)


def run():
    print("What problem are you facing right now?")
    query = input("> ").strip()

    matches = filter_busts(query)
    if matches == "No relevant busts found.":
        print(
            "\nNo past busts in the knowledge base yet. Run `buster bust` to add some!"
        )
        return

    print()
    on_task_done, finish = visual_loading(
        [
            "Searching your knowledge base",
            "Putting it into words",
        ]
    )

    suppress_stdout = contextlib.redirect_stdout(io.StringIO())
    suppress_stderr = contextlib.redirect_stderr(io.StringIO())

    try:
        logging.disable(logging.WARNING)
        with suppress_stdout, suppress_stderr:
            recall = Recall()
            recall._task_callback = on_task_done
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
    finally:
        logging.disable(logging.NOTSET)

    finish()
    print()
    print(result.raw)


if __name__ == "__main__":
    run()
