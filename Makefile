commands: # run the tool with the 'run' command
	uv run typer main.py run --help

db: # create the SQLite database file
	uv run typer main.py db

tool: # install the tool locally
	uv tool install .

ruff: # run ruff format and check
	rm -rf .ruff_cache
	uv run ruff format && uv run ruff check

clean_buster_dir: # remove the .buster directory
	rm -rf .buster

clean: # clean all generated cache files and directories
	rm -rf .ruff_cache __pycache__ 