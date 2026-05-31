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
    base = (
        "# T\n\n**Resolved:** yes\n\n## Problem\np\n\n"
        "## Solutions Tried\n- s\n\n## Lesson\nl\n\n## Tags\nt\n"
    )
    assert parse_md(base)["resolved"] is True
    assert parse_md(base.replace("yes", "no"))["resolved"] is False
