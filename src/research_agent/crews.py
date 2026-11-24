"""One small crew per pipeline stage, built from the YAML config."""

from pathlib import Path

import yaml
from crewai import Agent, Crew, Task
from crewai.tools import BaseTool
from pydantic import BaseModel

from research_agent.models import FactCheckReport, ResearchFindings, ResearchPlan
from research_agent.tools import scraping_tool, search_tool

CONFIG_DIR = Path(__file__).parent / "config"
AGENTS = yaml.safe_load((CONFIG_DIR / "agents.yaml").read_text())
TASKS = yaml.safe_load((CONFIG_DIR / "tasks.yaml").read_text())


def single_task_crew(
    agent_name: str,
    task_name: str,
    output_model: type[BaseModel] | None = None,
    tools: list[BaseTool] | None = None,
) -> Crew:
    agent = Agent(**AGENTS[agent_name], tools=tools or [], verbose=True)
    task = Task(**TASKS[task_name], agent=agent, output_pydantic=output_model)
    return Crew(agents=[agent], tasks=[task], verbose=True)


def planner_crew() -> Crew:
    return single_task_crew("research_planner", "planning_task", ResearchPlan)


def researcher_crew() -> Crew:
    return single_task_crew(
        "researcher",
        "research_task",
        ResearchFindings,
        tools=[search_tool, scraping_tool],
    )


def fact_checker_crew() -> Crew:
    return single_task_crew(
        "fact_checker",
        "fact_checking_task",
        FactCheckReport,
        tools=[search_tool, scraping_tool],
    )


def writer_crew() -> Crew:
    return single_task_crew("report_writer", "report_writing_task")
