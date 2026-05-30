from db.database import extract_keywords
from save import parse_md


def test_parse_md_fields():
    """parse_md correctly extracts every field from a well-formed MD string."""
    md = (
        "# Docker Daemon Issue\n\n"
        "**Resolved:** yes\n\n"
        "## Problem\nDocker daemon not running.\n\n"
        "## Solutions Tried\n- Mounted docker.sock\n- Restarted Docker\n\n"
        "## Lesson\nRemember: Mount the socket.\n\n"
        "## Tags\ndocker, daemon, socket\n"
    )
    data = parse_md(md)

    assert data["title"] == "Docker Daemon Issue"
    assert data["resolved"] is True
    assert "docker daemon not running" in data["problem"].lower()
    assert "Mounted docker.sock" in data["attempted_solutions"]
    assert "Restarted Docker" in data["attempted_solutions"]
    assert data["lesson"] == "Remember: Mount the socket."
    assert "docker" in data["tags"]


def test_parse_md_resolved_flag():
    """parse_md maps 'yes'/'no' to True/False for the resolved field."""
    base = "# T\n\n**Resolved:** yes\n\n## Problem\np\n\n## Solutions Tried\n- s\n\n## Lesson\nl\n\n## Tags\nt\n"
    assert parse_md(base)["resolved"] is True
    assert parse_md(base.replace("yes", "no"))["resolved"] is False


def test_extract_keywords_filters_stop_words():
    """Every word in the stop-word list is removed from keyword output."""
    stop_sample = ["the", "is", "and", "with", "from", "should"]
    for word in stop_sample:
        assert word not in extract_keywords(word), (
            f"Stop word '{word}' was not filtered out"
        )

    result = extract_keywords("the docker daemon is not running")
    assert "the" not in result
    assert "is" not in result
    assert "docker" in result
    assert "daemon" in result
    assert "running" in result


def test_extract_keywords_filters_short_words():
    """Words of 2 characters or fewer are dropped."""
    assert extract_keywords("go to db") == []
    assert "to" not in extract_keywords("connect to database")
    assert "db" not in extract_keywords("db connection failed")


def test_extract_keywords_lowercases_input():
    """Input is normalised to lowercase before filtering."""
    result = extract_keywords("Docker Daemon RUNNING")
    assert "docker" in result
    assert "daemon" in result
    assert "running" in result
    assert "Docker" not in result
