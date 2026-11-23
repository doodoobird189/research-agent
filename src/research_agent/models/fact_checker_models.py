from enum import Enum

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    SUPPORTED = "supported"  # confirmed by independent sources
    PARTIALLY_SUPPORTED = "partially_supported"  # broadly right, but detail is off
    CONTRADICTED = "contradicted"  # other reliable sources disagree
    OUTDATED = "outdated"  # was true, but superseded
    UNVERIFIABLE = "unverifiable"  # couldn't confirm or refute


class FindingCheck(BaseModel):
    finding_id: str = Field(description="ID of the finding being checked, e.g. 'F3'")
    verdict: Verdict
    confidence: float = Field(ge=0, le=1)
    reasoning: str = Field(description="Why this verdict was reached")
    evidence_urls: list[str] = Field(
        default_factory=list,
        description="Independent sources consulted while checking",
    )
    correction: str | None = Field(
        default=None,
        description="Corrected statement if partially supported, contradicted or outdated",
    )


class Contradiction(BaseModel):
    finding_ids: list[str]  # list of findings that conflict with each other
    description: str


class FactCheckReport(BaseModel):
    checks: list[FindingCheck]
    contradictions: list[Contradiction] = Field(default_factory=list)
    notes: str = ""
