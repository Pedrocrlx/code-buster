import os
import httpx
import typer

os.environ.setdefault("LITELLM_LOG", "ERROR")
os.environ.setdefault("OPENAI_API_KEY", "NA")  # required by litellm even for local models

from crewai import Agent, Crew, LLM, Task  # noqa: E402

OLLAMA_HOST = "http://localhost:11434"
MODEL = "ollama/qwen2.5:1.5b"

app = typer.Typer(add_completion=False)


def _check_ollama() -> bool:
    try:
        with httpx.Client(timeout=5.0) as client:
            return client.get(f"{OLLAMA_HOST}/api/tags").status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def _run(topic: str) -> str:
    llm = LLM(model=MODEL, base_url=OLLAMA_HOST, timeout=120.0)

    # Agents: give each a role, goal, and backstory (system prompt)
    researcher = Agent(role="Researcher", goal="Find key facts about the topic.", backstory="You are a concise, factual researcher.", llm=llm, verbose=False)
    writer     = Agent(role="Writer",     goal="Summarise the research clearly.",  backstory="You are a clear, brief technical writer.",  llm=llm, verbose=False)

    # Tasks: chain them with context= so the writer receives the researcher's output
    research = Task(description=f"List the five most important facts about: {topic}", expected_output="Five numbered facts, one sentence each.", agent=researcher)
    write    = Task(description="Write a two-paragraph summary of the research.",     expected_output="Two plain-prose paragraphs.",          agent=writer, context=[research])

    # Crew: runs tasks sequentially by default; swap to Process.hierarchical for a manager agent
    return str(Crew(agents=[researcher, writer], tasks=[research, write], verbose=False).kickoff())


@app.command()
def run(topic: str = typer.Argument(None, help="Topic to research (omit for interactive mode)")) -> None:
    """Researcher → Writer crew, powered by a local Qwen2.5 model."""
    typer.echo(f"Checking Ollama at {OLLAMA_HOST} ...")
    if not _check_ollama():
        typer.echo(f"Error: Ollama not reachable. Start it with:  ollama serve", err=True)
        raise typer.Exit(code=1)
    typer.echo("Ollama is active.\n")

    if topic:
        typer.echo(_run(topic))
        return

    typer.echo(f"Ready ({MODEL}). Enter a topic or 'quit'.\n")
    while True:
        t = input("Topic: ").strip()
        if not t: continue
        if t.lower() == "quit": break
        try:
            typer.echo(f"\n{_run(t)}\n")
        except Exception as e:
            typer.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    app()
