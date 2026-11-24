from pathlib import Path

import typer
from dotenv import load_dotenv

# Load API keys before importing the crew: the tools need them at import time.
load_dotenv()

from crewai.crews.crew_output import CrewOutput

from research_agent.crews.research_crew import ResearchCrew

app = typer.Typer(add_completion=False)


@app.command()
def research(
    topic: str,
    name: str = typer.Option(..., prompt="Report name"),
    output_dir: Path = Path("reports"),
) -> None:
    """Research TOPIC and save the report and findings to reports/NAME/."""
    run_dir = output_dir / name

    # Check before running the crew, so a taken name doesn't waste a whole run.
    if run_dir.exists():
        print(f"A report named '{name}' already exists. Choose a different name.")
        raise typer.Exit(code=1)

    result = ResearchCrew().crew().kickoff(inputs={"topic": topic})

    if not isinstance(result, CrewOutput):
        raise TypeError("Expected CrewOutput; is streaming enabled on the crew?")

    run_dir.mkdir(parents=True)

    # tasks_output follows task order: planning, research, fact check, report
    (run_dir / "report.md").write_text(result.raw)
    (run_dir / "findings.json").write_text(result.tasks_output[1].raw)
    (run_dir / "fact_check.json").write_text(result.tasks_output[2].raw)

    print(f"Saved to {run_dir}")


if __name__ == "__main__":
    app()
