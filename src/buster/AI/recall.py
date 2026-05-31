import contextlib
import io
import logging

from buster.AI.crew import Recall
from buster.AI.ui import visual_loading
from db.database import search_by_tags


# Function to filter busts based on user query, using keywords for matching
def filter_busts(query: str) -> str:
    keywords = query.lower().split()
    if not keywords:
        return "No relevant busts found."
    return search_by_tags(keywords)


# Questions the user to describe their current problem
# Searches the DB (knowledge base) for relevant past busts based on keywords
# Fails if no relevant busts are found, prompting user to add some with `buster bust`
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
