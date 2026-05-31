from crewai import LLM, Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel
from settings import OLLAMA_BASE_URL, OLLAMA_MODEL

# 0.0 = strict and deterministic, 1.0 = creative and unpredictable
local_model = LLM(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.2,
)


# Template for Organiser Output
# Ensures consistent structure for all bust entries
# NEcessary for readiblity and database storage
class BustEntry(BaseModel):
    title: str
    problem: str
    attempted_solutions: list[str]
    lesson: str
    tags: list[str]


@CrewBase
class Recall:
    """Recall crew"""

    agents_config = "config/recall_agents.yaml"
    tasks_config = "config/recall_tasks.yaml"
    agents: list[BaseAgent]
    tasks: list[Task]

    # @CrewBase replaces these strings with real dicts at runtime
    # mypy doesn't know that, so we tell it to ignore the indexing on each call
    # to avoid errors about 'str' not being subscriptable

    @agent
    def narrator(self) -> Agent:
        return Agent(
            config=self.agents_config["narrator"],  # type: ignore[index]
            llm=local_model,
            verbose=False,
        )

    @task
    def narrate(self) -> Task:
        return Task(
            config=self.tasks_config["narrate"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
            tracing=False,
        )


@CrewBase
class Buster:
    """Buster crew"""

    agents_config = "config/bust_agents.yaml"
    tasks_config = "config/bust_tasks.yaml"
    agents: list[BaseAgent]
    tasks: list[Task]
    _task_callback = None  # Is set externally before kickoff to drive the loading

    # Same deal as Recall — @CrewBase swaps strings for dicts, mypy can't see that

    @agent
    def processor(self) -> Agent:
        return Agent(
            config=self.agents_config["processor"],  # type: ignore[index]
            llm=local_model,
            verbose=False,
        )

    @agent
    def organizer(self) -> Agent:
        return Agent(
            config=self.agents_config["organizer"],  # type: ignore[index]
            llm=local_model,
            verbose=False,
        )

    @task
    def process(self) -> Task:
        return Task(
            config=self.tasks_config["process"],  # type: ignore[index]
        )

    @task
    def organise(self) -> Task:
        return Task(
            config=self.tasks_config["organise"],  # type: ignore[index]
            output_pydantic=BustEntry,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
            task_callback=self._task_callback,
            tracing=False,
        )
