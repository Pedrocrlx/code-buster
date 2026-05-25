from http.client import HTTPException

import typer
import sqlite3
import subprocess
from pathlib import Path
from db.database import init_db, fetch_all_busts, search_by_tags

app = typer.Typer(help="Code Buster CLI")


@app.command(name="setup")
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
    Create the .buster directory locally or in the user's home
    if the --global OR -g flag is used.
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
        ## Pull the ollama service and the qwen2.5 model
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
        result = subprocess.run(
            run_qwen2_5_model, capture_output=True, text=True, check=True
        )

        target_dir.mkdir(parents=True, exist_ok=True)
        typer.secho(
            f"Success: Directory .buster created {context} on: {target_dir}",
            fg=typer.colors.GREEN,
        )

    except Exception as e:
        typer.secho(f"Error creating folder: {e}", fg=typer.colors.RED, err=True)
    except FileNotFoundError:
        typer.secho(
            "Error: 'docker' command not found. Is Docker installed and in your PATH?",
            fg=typer.colors.RED,
        )
    except subprocess.CalledProcessError as e:
        typer.secho(f"An error occurred: {e}", fg=typer.colors.RED)
        typer.secho(f"Stderr: {e.stderr}", fg=typer.colors.RED)


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
        conn = sqlite3.connect(db_path)
        typer.secho(
            f"Success: Database created at {db_path}",
            fg=typer.colors.GREEN,
        )
    except HTTPException as e:
        typer.secho(f"Error creating database: {e}", fg=typer.colors.RED, err=True)


if __name__ == "__main__":
    app()
