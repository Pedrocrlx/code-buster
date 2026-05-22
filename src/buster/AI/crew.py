from pydantic import BaseModel
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

local_model = LLM(model="ollama/qwen2.5:1.5b", base_url="http://localhost:11434")


class IncidentEntry(BaseModel):
    title: str
    problem: str
    attempted_solutions: list[str]
    lesson: str
    tags: list[str]


@CrewBase
class Buster:
    """Buster crew"""

    agents: list[BaseAgent]
    tasks: list[Task]
    _task_callback = None

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
            output_pydantic=IncidentEntry,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
            task_callback=self._task_callback,
        )
