"""The research pipeline: plan -> research (in parallel) -> check sources -> fact-check -> write."""

import asyncio
import json

import httpx
from crewai.crews.crew_output import CrewOutput
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from research_agent.crews import (
    fact_checker_crew,
    planner_crew,
    researcher_crew,
    writer_crew,
)
from research_agent.models import (
    FactCheckReport,
    Finding,
    ResearchFindings,
    ResearchPlan,
)


class ResearchState(BaseModel):
    topic: str = ""
    objectives: list[str] = []
    findings: list[Finding] = []
    dead_link_findings: list[Finding] = []  # dropped: their source URL doesn't exist
    fact_check: FactCheckReport = FactCheckReport(checks=[])
    report: str = ""


class ResearchFlow(Flow[ResearchState]):
    @start()
    def plan(self) -> None:
        result = planner_crew().kickoff(inputs={"topic": self.state.topic})
        self.state.objectives = parse(result, ResearchPlan).research_topics

    @listen(plan)
    async def research(self) -> None:
        # One researcher per objective, all running at the same time.
        inputs = [
            {"topic": self.state.topic, "objective": objective}
            for objective in self.state.objectives
        ]
        results = await researcher_crew().akickoff_for_each(inputs=inputs)

        for objective, result in zip(self.state.objectives, results, strict=True):
            try:
                findings = parse(result, ResearchFindings).findings
            except TypeError:
                print(f"Skipping objective with unusable output: {objective}")
                continue
            for finding in findings:
                finding.objective = objective
                self.state.findings.append(finding)

    @listen(research)
    async def check_sources(self) -> None:
        # LLMs sometimes invent URLs. Drop any finding whose source doesn't exist.
        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
            checks = [link_exists(client, f.source_url) for f in self.state.findings]
            exists = await asyncio.gather(*checks)

        all_findings = self.state.findings
        self.state.findings = [f for f, ok in zip(all_findings, exists) if ok]
        self.state.dead_link_findings = [
            f for f, ok in zip(all_findings, exists) if not ok
        ]

        # Number the findings here, so IDs are unique across all researchers.
        for number, finding in enumerate(self.state.findings, start=1):
            finding.id = f"F{number}"

    @listen(check_sources)
    def fact_check(self) -> None:
        inputs = {"topic": self.state.topic, "findings": findings_json(self.state)}
        result = fact_checker_crew().kickoff(inputs=inputs)
        self.state.fact_check = parse(result, FactCheckReport)

    @listen(fact_check)
    def write(self) -> None:
        inputs = {
            "topic": self.state.topic,
            "findings": findings_json(self.state),
            "fact_check": self.state.fact_check.model_dump_json(indent=2),
        }
        result = writer_crew().kickoff(inputs=inputs)
        if not isinstance(result, CrewOutput):
            raise TypeError("Expected CrewOutput; is streaming enabled on the crew?")
        self.state.report = result.raw


def parse[T: BaseModel](result: object, model: type[T]) -> T:
    """Return a crew's structured output, checking it has the expected type."""
    if not isinstance(result, CrewOutput) or not isinstance(result.pydantic, model):
        raise TypeError(f"Crew did not return a valid {model.__name__}")
    return result.pydantic


def findings_json(state: ResearchState) -> str:
    return json.dumps([f.model_dump() for f in state.findings], indent=2)


async def link_exists(client: httpx.AsyncClient, url: str) -> bool:
    """False if the URL is malformed, its site doesn't respond, or the page is missing.

    Other errors (403, 429, 5xx) count as existing: many real sites block bots.
    """
    try:
        response = await client.get(url, follow_redirects=True, timeout=20)
    except httpx.HTTPError, httpx.InvalidURL:
        return False
    return response.status_code not in (404, 410)
