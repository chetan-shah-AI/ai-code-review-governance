from pydantic import BaseModel, Field


class AIReviewFinding(BaseModel):
    file_path: str | None = None
    line_number: int | None = None
    severity: str = Field(description="INFO, LOW, MEDIUM, HIGH, or CRITICAL")
    category: str
    title: str
    description: str
    recommendation: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class AIReviewResponse(BaseModel):
    findings: list[AIReviewFinding]