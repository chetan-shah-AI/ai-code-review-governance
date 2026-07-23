from app.agents.quality_review_agent import QualityReviewAgent
from app.schemas.llm import AIReviewFinding, AIReviewResponse
from app.schemas.review import DiffChunk, ReviewFileInput
from app.schemas.findings import Severity, SourceType


class FakeLLMClient:
    def review_code_chunk(self, system_prompt: str, user_prompt: str) -> AIReviewResponse:
        return AIReviewResponse(
            findings=[
                AIReviewFinding(
                    file_path="app/main.py",
                    line_number=10,
                    severity="LOW",
                    category="maintainability",
                    title="Unclear variable name",
                    description="The variable name is too vague.",
                    recommendation="Use a more descriptive variable name.",
                    confidence=0.8,
                )
            ]
        )


def test_quality_review_agent_converts_ai_response_to_findings():
    agent = QualityReviewAgent(llm_client=FakeLLMClient())

    review_file = ReviewFileInput(
        filename="app/main.py",
        file_type="source",
        status="modified",
        additions=5,
        deletions=1,
        chunks=[
            DiffChunk(
                file_path="app/main.py",
                chunk_index=0,
                start_line=1,
                end_line=20,
                content="+x = get_user()",
            )
        ],
    )

    findings = agent.review_file(review_file)

    assert len(findings) == 1
    assert findings[0].severity == Severity.LOW
    assert findings[0].source_type == SourceType.AI
    assert findings[0].tool_name == "quality_review_agent"