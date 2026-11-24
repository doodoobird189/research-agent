import json
from pathlib import Path

import typer
from dotenv import load_dotenv

# Load API keys before importing the flow: the tools need them at import time.
load_dotenv()

from research_agent.flow import ResearchFlow

app = typer.Typer(add_completion=False)


@app.command()
def research(
    topic: str,
    name: str = typer.Option(..., prompt="Report name"),
    output_dir: Path = Path("reports"),
) -> None:
    """Research TOPIC and save the report and findings to reports/NAME/."""
    run_dir = output_dir / name

    # Check before running the flow, so a taken name doesn't waste a whole run.
    if run_dir.exists():
        print(f"A report named '{name}' already exists. Choose a different name.")
        raise typer.Exit(code=1)

    flow = ResearchFlow()
    flow.kickoff(inputs={"topic": topic})
    state = flow.state

    run_dir.mkdir(parents=True)
    (run_dir / "report.md").write_text(state.report)
    (run_dir / "findings.json").write_text(to_json(state.findings))
    (run_dir / "fact_check.json").write_text(state.fact_check.model_dump_json(indent=2))
    (run_dir / "dead_links.json").write_text(to_json(state.dead_link_findings))

    print(f"Saved to {run_dir}")


def to_json(findings: list) -> str:
    return json.dumps([f.model_dump() for f in findings], indent=2)


if __name__ == "__main__":
    app()
