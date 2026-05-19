import typer
from pathlib import Path

app = typer.Typer(help="Buster CLI")


@app.command()
def init(
    is_global: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="Cria a pasta .buster na diretoria do utilizador (~/)",
    ),
    is_project: bool = typer.Option(
        True, "--project", "-p", help="Cria a pasta localmente"
    ),
):
    """
    Cria a pasta .buster localmente ou no utilizador se a flag --global for usada.
    """
    if is_global:
        target_dir = Path.home() / ".buster"
        contexto = "on user"
    else:
        target_dir = Path.cwd() / ".buster"
        contexto = "on context"

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        typer.secho(
            f"Success: Directory .buster created {contexto} on: {target_dir}",
            fg=typer.colors.GREEN,
        )

    except Exception as e:
        typer.secho(f"Error creating folder: {e}", fg=typer.colors.RED, err=True)


if __name__ == "__main__":
    app()
