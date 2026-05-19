commands:
	uv run typer main.py run --help

tool: # install the tool locally
	uv tool install .

ruff: # run ruff format and check
	uv run ruff format && uv run ruff check