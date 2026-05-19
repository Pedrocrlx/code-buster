import typer
from pathlib import Path

app = typer.Typer(help="Code Buster CLI")


@app.command()
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

        target_dir.mkdir(parents=True, exist_ok=True)
        typer.secho(
            f"Success: Directory .buster created {context} on: {target_dir}",
            fg=typer.colors.GREEN,
        )

    except Exception as e:
        typer.secho(f"Error creating folder: {e}", fg=typer.colors.RED, err=True)


if __name__ == "__main__":
    app()
