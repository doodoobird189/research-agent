"""Command-line entry point: run the research crew and save each run to its own folder."""

import re
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv

# API keys must be loaded before the crew is imported: the search and scraping
# tools are created at import time.
load_dotenv()

from crewai.crews.crew_output import CrewOutput

from research_agent.crews.research_crew import ResearchCrew

app = typer.Typer(add_completion=False)

MAX_SLUG_LENGTH = 50

# Task name -> file the task's structured output is saved to.
STRUCTURED_OUTPUTS = {
    "research_task": "findings.json",
    "fact_checking_task": "fact_check.json",
}


def slugify(text: str, max_length: int = MAX_SLUG_LENGTH) -> str:
    """Turn a research question into a short, filesystem-safe name."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(slug) > max_length:
        # Cut at the last whole word that fits.
        slug = slug[:max_length].rsplit("-", 1)[0]
    return slug or "report"


def make_run_dir(output_dir: Path, topic: str) -> Path:
    """Create a new folder like reports/2026-11-23_1432_what-is-rag/."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    base = output_dir / f"{timestamp}_{slugify(topic)}"

    run_dir = base
    counter = 2
    while run_dir.exists():  # same topic started twice in the same minute
        run_dir = base.with_name(f"{base.name}-{counter}")
        counter += 1

    run_dir.mkdir(parents=True)
    return run_dir


def save_outputs(result: CrewOutput, run_dir: Path) -> None:
    """Write the report and each task's structured output into the run folder."""
    (run_dir / "report.md").write_text(result.raw, encoding="utf-8")

    outputs_by_task = {output.name: output for output in result.tasks_output}
    for task_name, filename in STRUCTURED_OUTPUTS.items():
        output = outputs_by_task.get(task_name)
        if output is None:
            continue
        if output.pydantic is not None:
            content = output.pydantic.model_dump_json(indent=2)
        else:
            # Structured parsing failed; keep the raw text so nothing is lost.
            content = output.raw
            filename = Path(filename).with_suffix(".txt").name
        (run_dir / filename).write_text(content, encoding="utf-8")


@app.command()
def research(
    topic: Annotated[str, typer.Argument(help="The research question to investigate.")],
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            "-d",
            help="Parent folder for auto-named run folders.",
        ),
    ] = Path("reports"),
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Exact folder for this run, instead of an auto-generated name.",
        ),
    ] = None,
) -> None:
    """Research TOPIC and save a cited report plus the structured findings."""
    if output is not None:
        if output.exists() and any(output.iterdir()):
            raise typer.BadParameter(
                f"{output} already exists and is not empty.", param_hint="--output"
            )
        output.mkdir(parents=True, exist_ok=True)
        run_dir = output
    else:
        run_dir = make_run_dir(output_dir, topic)

    result = ResearchCrew().crew().kickoff(inputs={"topic": topic})

    if not isinstance(result, CrewOutput):
        raise TypeError("Expected CrewOutput; is streaming enabled on the crew?")

    save_outputs(result, run_dir)
    typer.echo(f"\nSaved to {run_dir}/")
    for path in sorted(run_dir.iterdir()):
        typer.echo(f"  {path.name}")


if __name__ == "__main__":
    app()
