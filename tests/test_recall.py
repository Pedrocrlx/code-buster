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
    """Vague recall: 'postgres startup' surfaces the database connection bust
    using indirect terms without naming the exact error directly.
    Test fails if the database bust is not found."""
    query = "postgres startup"
    matches = filter_busts(query)

    assert matches != "No relevant busts found.", "No match for vague query"
    assert "psycopg2" in matches.lower() or "database" in matches.lower(), (
        "Database incident not in matches"
    )
    assert "devcontainer" not in matches.lower(), (
        "Wrong incident (Docker) returned for postgres query"
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
