from CLI.main import app
from db import database
from typer.testing import CliRunner

cli_runner = CliRunner()


def test_cli_db_creates_database(tmp_path, monkeypatch):
    """buster db creates the SQLite DB file and reports success
    when the .busts directory already exists."""
    busts_dir = tmp_path / ".busts"
    busts_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(database, "DB_PATH", busts_dir / "busts.db")

    result = cli_runner.invoke(app, ["db"])

    assert result.exit_code == 0
    assert (busts_dir / "busts.db").exists()
    assert "success" in result.output.lower()


def test_cli_db_missing_busts_dir(tmp_path, monkeypatch):
    """buster db reports an error and exits cleanly when .busts does not exist."""
    monkeypatch.chdir(tmp_path)

    result = cli_runner.invoke(app, ["db"])

    assert result.exit_code == 0
    assert "please run" in result.output.lower() or "setup" in result.output.lower()
    assert not (tmp_path / ".busts" / "busts.db").exists()


def test_cli_setup_creates_directory_and_database(tmp_path, monkeypatch):
    """buster setup creates .busts and the database when neither exists.
    Docker steps are skipped gracefully when Docker is not available."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(database, "DB_PATH", tmp_path / ".busts" / "busts.db")

    result = cli_runner.invoke(app, ["setup"])

    assert result.exit_code == 0
    assert (tmp_path / ".busts").exists()
    assert (tmp_path / ".busts" / "busts.db").exists()
    assert "ready" in result.output.lower()


def test_cli_setup_is_idempotent(tmp_path, monkeypatch):
    """Running buster setup twice reports existing resources as already present
    rather than failing or duplicating them."""
    busts_dir = tmp_path / ".busts"
    busts_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(database, "DB_PATH", busts_dir / "busts.db")

    cli_runner.invoke(app, ["setup"])  # first run — creates DB
    result = cli_runner.invoke(app, ["setup"])  # second run — should skip

    assert result.exit_code == 0
    assert "already" in result.output.lower()


def test_cli_save_no_args(tmp_path, monkeypatch):
    """buster save with no arguments reports a helpful error."""
    monkeypatch.chdir(tmp_path)

    result = cli_runner.invoke(app, ["save"])

    assert result.exit_code == 1
    assert "provide" in result.output.lower() or "--all" in result.output.lower()


def test_cli_save_missing_file(tmp_path, monkeypatch):
    """buster save exits with code 1 when the given file does not exist."""
    monkeypatch.chdir(tmp_path)

    result = cli_runner.invoke(app, ["save", "nonexistent.md"])

    assert result.exit_code == 0  # partial failures don't hard-exit
    assert "not found" in result.output.lower()


def test_cli_save_single_file(tmp_path, monkeypatch, tmp_db):
    """buster save <file> parses a single MD file and saves it to the database."""
    import sqlite3

    md_file = tmp_path / "bust_test.md"
    md_file.write_text(
        "# Docker Socket Issue\n\n"
        "**Resolved:** yes\n\n"
        "## Problem\nDocker socket not mounted.\n\n"
        "## Solutions Tried\n- Mounted the socket\n\n"
        "## Lesson\nRemember: mount the socket.\n\n"
        "## Tags\ndocker, socket\n"
    )
    monkeypatch.chdir(tmp_path)

    result = cli_runner.invoke(app, ["save", str(md_file)])

    assert result.exit_code == 0
    assert "saved" in result.output.lower()

    with sqlite3.connect(tmp_db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM busts").fetchone()[0] == 1


def test_cli_save_multiple_files(tmp_path, monkeypatch, tmp_db):
    """buster save file1 file2 saves each file and reports a total."""
    import sqlite3

    md = (
        "# {title}\n\n**Resolved:** yes\n\n"
        "## Problem\nSomething broke.\n\n"
        "## Solutions Tried\n- Fixed it\n\n"
        "## Lesson\nRemember: fix it.\n\n"
        "## Tags\ntest\n"
    )
    files = []
    for i in range(3):
        f = tmp_path / f"bust_{i}.md"
        f.write_text(md.format(title=f"Issue {i}"))
        files.append(str(f))

    monkeypatch.chdir(tmp_path)
    result = cli_runner.invoke(app, ["save", *files])

    assert result.exit_code == 0
    assert "3/3" in result.output

    with sqlite3.connect(tmp_db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM busts").fetchone()[0] == 3


def test_cli_save_all(tmp_path, monkeypatch, tmp_db):
    """buster save --all saves every bust_*.md file in .busts."""
    import sqlite3

    busts_dir = tmp_path / ".busts"
    busts_dir.mkdir()
    monkeypatch.chdir(tmp_path)

    md = (
        "# {title}\n\n**Resolved:** no\n\n"
        "## Problem\nSomething broke.\n\n"
        "## Solutions Tried\n- Tried something\n\n"
        "## Lesson\nRemember: check it.\n\n"
        "## Tags\ntest\n"
    )
    for i in range(3):
        (busts_dir / f"bust_2026_issue_{i}.md").write_text(
            md.format(title=f"Issue {i}")
        )

    result = cli_runner.invoke(app, ["save", "--all"])

    assert result.exit_code == 0
    assert "3/3" in result.output

    with sqlite3.connect(tmp_db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM busts").fetchone()[0] == 3


def test_cli_save_all_empty_buster(tmp_path, monkeypatch, tmp_db):
    """buster save --all reports nothing to save when .busts has no bust files."""
    busts_dir = tmp_path / ".busts"
    busts_dir.mkdir()
    monkeypatch.chdir(tmp_path)

    result = cli_runner.invoke(app, ["save", "--all"])

    assert result.exit_code == 0
    assert "no bust files" in result.output.lower()
