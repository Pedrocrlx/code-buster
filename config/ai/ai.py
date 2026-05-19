from crewai import Agent, Crew, Task

MODEL = "ollama/qwen2.5:0.5b"

agent = Agent(
    role="Assistant",
    goal="Give helpful and concise answers.",
    backstory="A knowledgeable and friendly AI assistant.",
    llm=MODEL,
    verbose=False,
)

while True:
    message = input("You: ").strip()

    if message in ("quit", "exit"):
        break

    if message:
        task = Task(description=message, expected_output="A helpful response.", agent=agent)
        print(Crew(agents=[agent], tasks=[task], verbose=False).kickoff())
