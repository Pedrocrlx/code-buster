import sys
import threading
import time

from crewai import Agent, Crew, LLM, Task

llm = LLM(model="ollama/qwen2.5:0.5b", base_url="http://host.docker.internal:11434")

agent = Agent(
    role="Assistant",
    goal="Give helpful and concise answers.",
    backstory="A knowledgeable and friendly AI assistant.",
    llm=llm,
    verbose=False,
)


def loading_animation(stop: threading.Event) -> None:
    frames = ["|", "/", "-", "\\"]
    i = 0
    while not stop.is_set():
        sys.stdout.write(f"\r{frames[i % len(frames)]}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r \r")
    sys.stdout.flush()


while True:
    message = input("You: ").strip() # Get user input and remove leading/trailing whitespace

    if message in ("quit", "exit"): 
        break # Exit the loop if the user types "quit" or "exit"

    if not message:
        continue # Skip empty input, tries input again

    stop = threading.Event()
    loader = threading.Thread(target=loading_animation, args=(stop,), daemon=True)
    loader.start()

    try:
        result = Crew(
            agents=[agent],
            tasks=[Task(description=message, expected_output="A helpful response.", agent=agent)],
            verbose=False,
        ).kickoff()
    finally:
        stop.set()
        loader.join()

    print(result)
