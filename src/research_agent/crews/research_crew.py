from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from research_agent.models import FactCheckReport, ResearchFindings, ResearchPlan
from research_agent.tools import scraping_tool, search_tool


@CrewBase
class ResearchCrew:
    agents_config: dict[str, Any] = "../config/agents.yaml"
    tasks_config: dict[str, Any] = "../config/tasks.yaml"

    # Agents

    @agent
    def research_planner(self) -> Agent:
        return Agent(config=self.agents_config["research_planner"], verbose=True)

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            verbose=True,
            tools=[search_tool, scraping_tool],
        )

    @agent
    def fact_checker(self) -> Agent:
        return Agent(
            config=self.agents_config["fact_checker"],
            verbose=True,
            tools=[search_tool, scraping_tool],
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(config=self.agents_config["report_writer"], verbose=True)

    # Tasks
    @task
    def planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["planning_task"],
            agent=self.research_planner(),
            output_pydantic=ResearchPlan,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.researcher(),
            output_pydantic=ResearchFindings,
        )

    @task
    def fact_checking_task(self) -> Task:
        return Task(
            config=self.tasks_config["fact_checking_task"],
            agent=self.fact_checker(),
            output_pydantic=FactCheckReport,
        )

    @task
    def report_writing_task(self) -> Task:
        return Task(
            config=self.tasks_config["report_writing_task"],
            agent=self.report_writer(),
            output_file="report.md",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # automatically collected via @agent
            tasks=self.tasks,  # automatically collected via @tasks
            process=Process.sequential,
            verbose=True,
        )
