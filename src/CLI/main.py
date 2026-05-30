import sqlite3
import subprocess
from pathlib import Path

import typer

from buster.AI.main import run as bust_run
from buster.AI.recall import run as recall_run
from buster.AI.save import parse_md
from db.database import init_db, save_bust

app = typer.Typer(help="Code Buster CLI")


@app.command(name="setup")
def setup():
    """
    First-time setup: create the .buster directory, start Ollama,
    pull the qwen2.5:1.5b model, and initialise the database.
    Safe to re-run — already-completed steps are skipped.
    """
    target_dir = Path.cwd() / ".buster"
    db_path = target_dir / "buster.db"

    typer.echo("Setting up Code Buster...\n")

    # Step 1 — .buster directory
    typer.echo("[1/4] Creating .buster directory...")
    if target_dir.exists():
        typer.secho(f"      Already exists at {target_dir}", fg=typer.colors.YELLOW)
    else:
        target_dir.mkdir(parents=True)
        typer.secho(f"      Created at {target_dir}", fg=typer.colors.GREEN)

    # Step 2 — Ollama service
    typer.echo("[2/4] Starting Ollama service...")
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d", "ollama"],
            check=True,
            capture_output=True,
        )
        typer.secho("      Ollama service running.", fg=typer.colors.GREEN)
    except FileNotFoundError:
        typer.secho(
            "      Docker not found — skipping. Start Ollama manually if needed.",
            fg=typer.colors.YELLOW,
        )
    except subprocess.CalledProcessError as e:
        typer.secho(
            f"      Could not start Ollama via Docker: {e.stderr.strip() or e}",
            fg=typer.colors.YELLOW,
        )
        typer.secho(
            "      Skipping. Start Ollama manually if it is not already running.",
            fg=typer.colors.YELLOW,
        )

    # Step 3 — model pull (output not suppressed — can take several minutes)
    # Change model name here if switching models. Keep in sync with OLLAMA_MODEL default in crew.py.
    typer.echo("[3/4] Pulling qwen2.5:1.5b model (this may take a few minutes)...")
    try:
        subprocess.run(
            ["docker", "compose", "exec", "ollama", "ollama", "pull", "qwen2.5:1.5b"],
            check=True,
        )
        typer.secho("      Model ready.", fg=typer.colors.GREEN)
    except FileNotFoundError:
        typer.secho(
            "      Docker not found — skipping. Pull the model manually if needed.",
            fg=typer.colors.YELLOW,
        )
    except subprocess.CalledProcessError as e:
        typer.secho(
            f"      Could not pull model via Docker: {e}",
            fg=typer.colors.YELLOW,
        )
        typer.secho(
            "      Skipping. Run `ollama pull qwen2.5:1.5b` manually if needed.",
            fg=typer.colors.YELLOW,
        )

    # Step 4 — database
    typer.echo("[4/4] Initialising database...")
    if db_path.exists():
        typer.secho(f"      Already exists at {db_path}", fg=typer.colors.YELLOW)
    else:
        try:
            init_db()
            typer.secho(f"      Database created at {db_path}", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(
                f"      Failed to create database: {e}", fg=typer.colors.RED, err=True
            )
            raise typer.Exit(1)

    typer.echo("")
    typer.secho(
        "Code Buster is ready. Run `buster bust` to log your first incident.",
        fg=typer.colors.GREEN,
    )


@app.command(name="init")
def init(
    is_global: bool = typer.Option(
        False, "--global", "-g", help="Create directory on user home (~/)"
    ),
    is_project: bool = typer.Option(
        True,
        "--project",
        "-p",
        help="Create directory locally (current working directory)",
    ),
):
    """
    Create the .buster directory locally or in the user home.
    Options globally: --global -g
    Option locally: -p
    Pull the ollama service
    and the qwen2.5 model using Docker Compose.
    """
    if is_global:
        target_dir = Path.home() / ".buster"
        context = "on user"
    else:
        target_dir = Path.cwd() / ".buster"
        context = "on context"

    try:
        if target_dir.exists():
            typer.secho(
                f"Directory .buster already exists {context} on: {target_dir}",
                fg=typer.colors.YELLOW,
            )
        pull_ollama_service = ["docker", "compose", "up", "-d", "ollama"]
        subprocess.run(pull_ollama_service, check=True)

        run_qwen2_5_model = [
            "docker",
            "compose",
            "exec",
            "ollama",
            "ollama",
            "pull",
            "qwen2.5:1.5b",
        ]
        subprocess.run(run_qwen2_5_model, capture_output=True, text=True, check=True)

        target_dir.mkdir(parents=True, exist_ok=True)
        typer.secho(
            f"Success: Directory .buster created {context} on: {target_dir}",
            fg=typer.colors.GREEN,
        )

    except FileNotFoundError:
        typer.secho(
            "Error: 'docker' command not found. Is Docker installed and in your PATH?",
            fg=typer.colors.RED,
            err=True,
        )
    except subprocess.CalledProcessError as e:
        typer.secho(f"An error occurred: {e}", fg=typer.colors.RED, err=True)
        typer.secho(f"Stderr: {e.stderr}", fg=typer.colors.RED, err=True)
    except Exception as e:
        typer.secho(f"Error creating folder: {e}", fg=typer.colors.RED, err=True)


@app.command(name="db")
def create_db():
    """
    Create the SQLite database file in the .buster directory.
    """
    target_dir = Path.cwd() / ".buster"
    db_path = target_dir / "buster.db"

    if not target_dir.exists():
        typer.secho(
            "Please run 'setup' command first.",
            fg=typer.colors.RED,
            err=True,
        )
        return

    if db_path.exists():
        typer.secho(
            f"Database already exists at {db_path}",
            fg=typer.colors.YELLOW,
        )
        return

    try:
        init_db()
        sqlite3.connect(db_path)
        typer.secho(
            f"Success: Database created at {db_path}",
            fg=typer.colors.GREEN,
        )
    except Exception as e:
        typer.secho(f"Error creating database: {e}", fg=typer.colors.RED, err=True)


@app.command(name="bust")
def record_bust():
    """
    Run bust into agents (CrewAI) and output markdown file.
    """
    try:
        busts_dir = Path.cwd() / ".buster"
        if not busts_dir.exists():
            typer.secho(
                f"Error: .buster directory not found at {busts_dir}",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(1)
        bust_run(busts_dir=busts_dir)
    except KeyboardInterrupt:
        typer.secho("\nBust cancelled by user.", fg=typer.colors.YELLOW)
        raise typer.Exit()
    except Exception as e:
        typer.secho(f"Error during bust: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command(name="save")
def record_save(
    files: list[Path] | None = typer.Argument(
        None,
        help="One or more .md bust files to save. Omit when using --all.",
    ),
    all_: bool = typer.Option(
        False,
        "--all",
        help="Save every bust_*.md file found in the .buster directory.",
    ),
):
    """
    Parse bust markdown file(s) and save them to the database.

    \b
    Single file:    buster save .buster/bust_<timestamp>_<slug>.md
    Multiple files: buster save file1.md file2.md file3.md
    All in .buster: buster save --all
    """
    if not files and not all_:
        typer.secho(
            "Provide at least one file, or use --all to save every bust in .buster.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)

    if all_:
        buster_dir = Path.cwd() / ".buster"
        if not buster_dir.exists():
            typer.secho(
                "No .buster directory found. Run `buster setup` first.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(1)
        # Glob pattern must match the filename prefix written by main.py ("bust_").
        # If you change the prefix there, update this pattern to match.
        targets = sorted(buster_dir.glob("bust_*.md"))
        if not targets:
            typer.secho("No bust files found in .buster.", fg=typer.colors.YELLOW)
            return
    else:
        targets = list(files)

    saved = 0
    for path in targets:
        if not path.exists():
            typer.secho(
                f"  Skipped: file not found — {path}", fg=typer.colors.RED, err=True
            )
            continue

        data = parse_md(path.read_text())

        if not data["title"]:
            typer.secho(
                f"  Skipped {path.name}: could not parse title.",
                fg=typer.colors.YELLOW,
            )
            continue

        try:
            bust_id = save_bust(data)
            typer.secho(f"  Bust #{bust_id} saved — {path.name}", fg=typer.colors.GREEN)
            saved += 1
        except Exception as e:
            typer.secho(
                f"  Error saving {path.name}: {e}", fg=typer.colors.RED, err=True
            )

    if len(targets) > 1:
        typer.echo(f"\n{saved}/{len(targets)} files saved.")


@app.command(name="recall")
def search_busts():
    """
    Search past incidents for a similar problem.
    """
    try:
        recall_run()
    except KeyboardInterrupt:
        typer.secho("\nRecall cancelled by user.", fg=typer.colors.YELLOW)
        raise typer.Exit()
    except Exception as e:
        typer.secho(f"Error during recall: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
