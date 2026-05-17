import typer
from crewai import Agent, Crew, Task

MODEL = "ollama/qwen2.5:1.5b"
app = typer.Typer(add_completion=False)


def _run(topic: str) -> str:
    # Agents: role + goal + backstory define the persona
    researcher = Agent(
        role="Researcher",
        goal="Find key facts.",
        backstory="Concise factual researcher.",
        llm=MODEL,
        verbose=False,
    )
    writer = Agent(
        role="Writer",
        goal="Summarise clearly.",
        backstory="Brief technical writer.",
        llm=MODEL,
        verbose=False,
    )

    # Tasks: context= pipes the previous task's output into the next
    research_task = Task(
        description=f"Five key facts about: {topic}",
        expected_output="Five numbered facts.",
        agent=researcher,
    )
    writing_task = Task(
        description="Two-paragraph summary of the research.",
        expected_output="Two paragraphs.",
        agent=writer,
        context=[research_task],
    )

    # Crew: sequential by default; kickoff() blocks until all tasks finish
    return str(
        Crew(
            agents=[researcher, writer],
            tasks=[research_task, writing_task],
            verbose=False,
        ).kickoff()
    )


@app.command()
def run(
    topic: str = typer.Argument(
        None, help="Topic to research (omit for interactive mode)"
    ),
) -> None:
    """Researcher → Writer crew via local Ollama."""
    if topic:
        typer.echo(_run(topic))
        return

    typer.echo(f"Ready ({MODEL}). Enter a topic or 'quit'.\n")
    while (topic := input("Topic: ").strip()) != "quit":
        if topic:
            typer.echo(f"\n{_run(topic)}\n")


if __name__ == "__main__":
    app()
