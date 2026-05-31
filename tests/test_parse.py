from pathlib import Path

from save import parse_md

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_md_fields():
    """parse_md correctly extracts every field from the resolved fixture."""
    data = parse_md((FIXTURES_DIR / "resolved.md").read_text())

    assert data["title"] == "Docker Daemon Not Running in Devcontainer"
    assert data["resolved"] is True
    assert "docker daemon not running" in data["problem"].lower()
    assert any("docker.sock" in s.lower() for s in data["attempted_solutions"])
    assert data["lesson"]
    assert "docker" in data["tags"]


def test_parse_md_resolved_flag():
    """parse_md maps 'yes'/'no' to True/False using the two hardcoded fixtures."""
    assert parse_md((FIXTURES_DIR / "resolved.md").read_text())["resolved"] is True
    assert parse_md((FIXTURES_DIR / "unresolved.md").read_text())["resolved"] is False
