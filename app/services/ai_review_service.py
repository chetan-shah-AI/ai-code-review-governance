from app.agents.quality_review_agent import QualityReviewAgent
from app.schemas.findings import Finding
from app.schemas.review import ReviewInput


def run_ai_quality_review(
    review_input: ReviewInput,
    agent: QualityReviewAgent | None = None,
) -> list[Finding]:
    """
    Run AI quality review for all reviewable files.
    """

    quality_agent = agent or QualityReviewAgent()

    findings: list[Finding] = []

    for review_file in review_input.files:
        if review_file.file_type not in {"source", "test"}:
            continue

        file_findings = quality_agent.review_file(review_file)
        findings.extend(file_findings)

    return findings