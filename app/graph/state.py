from typing import TypedDict

from app.schemas.findings import Finding, ToolResult
from app.schemas.review import ReviewInput
from app.services.verdict_service import Verdict


class ReviewGraphState(TypedDict):
    review_input: ReviewInput

    deterministic_findings: list[Finding]

    ai_findings: list[Finding]

    governance_findings: list[Finding]

    all_findings: list[Finding]

    verdict: str

    summary: str