from crew import Recall
from recall import filter_busts

from example_busts import ollama


def test_filter_busts_stop_words_only_query(busted_db):
    """A query made entirely of stop words produces no keyword matches."""
    assert filter_busts("the is and with") == "No relevant busts found."


@ollama
def test_recall_direct_query(busted_db):
    """Direct recall: 'docker daemon' targets and surfaces the devcontainer
    incident. Test fails if the Docker incident is not found."""
    query = "docker daemon"
    matches = filter_busts(query)

    assert matches != "No relevant busts found.", "No match for direct query"
    assert "docker" in matches.lower(), "Docker incident not in matches"
    assert "rebase" not in matches.lower(), "Wrong incident (Git) returned for docker query"

    result = Recall().crew().kickoff(
        inputs={"query": query, "matches": matches, "today": "2026-05-24"}
    )

    assert result.raw.strip(), "Recall crew returned empty output"


@ollama
def test_recall_vague_query(busted_db):
    """Vague recall: 'pipeline deployment' surfaces the Git rebase incident
    using terms from its problem description, not its title.
    Test fails if the Git incident is not found."""
    query = "pipeline deployment"
    matches = filter_busts(query)

    assert matches != "No relevant busts found.", "No match for vague query"
    assert "pipeline" in matches.lower() or "rebase" in matches.lower(), (
        "Git rebase incident not in matches"
    )
    assert "devcontainer" not in matches.lower(), (
        "Wrong incident (Docker) returned for pipeline query"
    )

    result = Recall().crew().kickoff(
        inputs={"query": query, "matches": matches, "today": "2026-05-24"}
    )

    assert result.raw.strip(), "Recall crew returned empty output"


@ollama
def test_inexistent_recall(busted_db):
    """Querying a topic absent from the DB returns no matches.
    Test fails if any existing bust is recalled."""
    query = "bluetooth device pairing"
    matches = filter_busts(query)

    assert matches == "No relevant busts found.", (
        f"Expected no matches for unrelated query, got: {matches}"
    )

    result = Recall().crew().kickoff(
        inputs={"query": query, "matches": matches, "today": "2026-05-24"}
    )

    assert "nothing similar" in result.raw.lower(), (
        "Recall crew should report nothing found for an unrelated query"
    )
