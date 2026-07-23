from typing import Any

from pydantic import BaseModel, Field


class PublishRequest(BaseModel):
    """
    Information required to publish a review
    to a GitHub Pull Request.
    """

    repo_full_name: str
    pr_number: int
    verdict: str
    summary: str

    findings: list[Any] = Field(
        default_factory=list
    )


class PublishResult(BaseModel):
    """
    Result returned after attempting to publish
    a GitHub Pull Request comment.
    """

    success: bool
    status: str
    repository: str
    pr_number: int

    comment_id: int | None = None
    comment_url: str | None = None
    message: str | None = None