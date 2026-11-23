# Multi-Agent Research System

Imagine a user asks:
"Research the current state of humanoid robotics, identifythe leading companies, analyse the technologies they're developing, and produce a report on future opportunities."

There will be 5 agents working together.

## Agent 1: Reserach Planner

**Role:** Reserach Strategist

Before anyone starts researching, this agent breaks the user's question into smaller research objectives.

Responsibilities:

- Understand the research question
- Identify important subtopics
- Determine what information needs to be collected
- Delegate research objectives to the reseacher

Tools:

- LLM (no external tools necessarily).

Example output:

```json
{
  "research_topics": [
    "Leading humanoid robotics companies",
    "Current robotics hardware",
    "AI models used in robotics",
    "Commercial applications",
    "Future market opportunities"
  ]
}
```

## Agent 2: Researcher

**Role:** Internet Research Specialist

This is the primary researcher.

Responsibilities:

- Search the internet for relevant information.
- Find articles, reports, research papers and documentation.
- Extract relevant information.
- Collect URLs and publication dates.
- Return structured research findings.

Tools:

- `SerperDevTool` - Google search results.
- `ScrapeWebsiteTool` - Extract website content.
- `Firecrawl` - More sophisticate website crawling.
- `WikipediaTools` - General background information.

__Note: This agent is only responsible for collecting information, not deciding whether the information is correct, or writing reports.__Note

## Agent 3: Fact Checker

**Role:** Research Verification Specialist

This agent verifies the information gathered by the Researcher agent.

Responsibilities:

- Verify claims made by the researcher.
- Cross-reference information against independent sources.
- Identify contradictory information.
- Flag outdated statistics.
- Distinguish factual claims from speculation.
- Assign confidence levels to findings.

Tools:

- `SerperDevTool` - Search for independent corroboration.
- `ScrapeWebsiteTool` - Inspect original sources.

For example, the researcher agent might report:

_"Tesla plans to produce one million Optimus robots annually by 2030."_

The fact checker agent investigates whether this is an actual commitment, an executive prediction or simply speculation reported by media outlets.

## Agent 4: Analyst

**Role:** Research Analyst

This agent interprets the researcher's findings (after it has been fact checked).

Responsibilities:

- Identify patterns and trends.
- Compare competing companies and technologies.
- Identify opportunities and challenges.
- Draw conclusions from the collected information.
- Identify gaps in the available research.

Tools:

- LLM.
- Python execution tool (maybe?).
- Calculator.
- Possible access to structured datasets.

For example, it might identify that humanoid robotics companies are increasingly focusing on warehouse automation because it offers a more controlled environment than domestic applications.

## Agent 5: Report Writer

**Role:** Technical Research Writer

Responsibilities:

- Take the verified research and analyst findings.
- Organise the information into logical sections
- Produce an executive summary.
- Write a comprehensive report.
- Include citations and references.
- Generate a final Markdown document or PDF.

Tools:

- File writing tool.
- Python (for PDF generation, charts, etc.).
