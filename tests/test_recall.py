from crew import Recall
from recall import filter_busts

from example_busts import ollama


@ollama
def test_recall_direct_query(busted_db):
    """Direct recall: 'docker daemon' targets and surfaces the devcontainer
    incident. Test fails if the Docker incident is not found."""
    query = "docker daemon"
    matches = filter_busts(query)

    assert matches != "No relevant busts found.", "No match for direct query"
    assert "docker" in matches.lower(), "Docker incident not in matches"
    assert "rebase" not in matches.lower(), (
        "Wrong incident (Git) returned for docker query"
    )

    result = Recall().crew().kickoff(inputs={"query": query, "matches": matches})

    assert result.raw.strip(), "Recall crew returned empty output"


@ollama
def test_recall_vague_query(busted_db):
    """Vague recall: 'git pipeline' surfaces the Git rebase bust
    using two of its tags without naming rebase or conflict directly.
    Test fails if the Git bust is not found."""
    query = "git pipeline"
    matches = filter_busts(query)

    assert matches != "No relevant busts found.", "No match for vague query"
    assert "pipeline" in matches.lower() or "rebase" in matches.lower(), (
        "Git rebase incident not in matches"
    )
    assert "devcontainer" not in matches.lower(), (
        "Wrong incident (Docker) returned for pipeline query"
    )

    result = Recall().crew().kickoff(inputs={"query": query, "matches": matches})

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

    result = Recall().crew().kickoff(inputs={"query": query, "matches": matches})

    assert "nothing similar" in result.raw.lower(), (
        "Recall crew should report nothing found for an unrelated query"
    )
