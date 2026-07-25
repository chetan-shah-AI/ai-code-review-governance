from typing import Any, TypedDict

from app.schemas.review import ReviewInput


class ReviewGraphState(
    TypedDict,
    total=False,
):
    """
    Shared state used by the LangGraph workflow.
    """

    review_input: ReviewInput

    classified_files: list[Any]
    deterministic_findings: list[Any]
    ai_findings: list[Any]
    governance_findings: list[Any]
    all_findings: list[Any]

    verdict: Any
    summary: Any

    publish_enabled: bool
    publish_markdown: str
    publish_result: dict[str, Any]