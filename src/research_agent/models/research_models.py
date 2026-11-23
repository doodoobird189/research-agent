from pydantic import BaseModel


class ResearchPlan(BaseModel):
    research_topics: list[str]


class Finding(BaseModel):
    id: str  # e.g. "F1", "F2"
    claim: str  # the specific statement
    objective: str
    details: str  # full context - can be as long as needed
    quote: str | None  # verbatim quote from source
    source_url: str
    source_title: str | None
    published_date: str | None


class ResearchFindings(BaseModel):
    findings: list[Finding]
    notes: str  # catch all for anything that didnt fit above


# hopefully not too rigid to cause information loss
