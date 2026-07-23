from app.schemas.findings import Finding, Severity, SourceType
from app.schemas.review import ReviewInput, ReviewFileInput, DiffChunk
from app.services.ai_review_service import run_ai_quality_review


class FakeQualityAgent:
    def review_file(self, review_file):
        return [
            Finding(
                file_path=review_file.filename,
                line_number=1,
                severity=Severity.LOW,
                category="quality",
                title="Fake quality issue",
                description="Fake issue for testing.",
                recommendation="Fix fake issue.",
                source_type=SourceType.AI,
                tool_name="quality_review_agent",
                confidence=0.9,
            )
        ]


def test_ai_review_service_reviews_only_source_and_test_files():
    review_input = ReviewInput(
        repo_full_name="raja/example-repo",
        pr_number=12,
        files=[
            ReviewFileInput(
                filename="app/main.py",
                file_type="source",
                status="modified",
                additions=5,
                deletions=0,
                chunks=[
                    DiffChunk(
                        file_path="app/main.py",
                        chunk_index=0,
                        content="+print('hello')",
                    )
                ],
            ),
            ReviewFileInput(
                filename="README.md",
                file_type="docs",
                status="modified",
                additions=2,
                deletions=0,
                chunks=[
                    DiffChunk(
                        file_path="README.md",
                        chunk_index=0,
                        content="+docs update",
                    )
                ],
            ),
        ],
    )

    findings = run_ai_quality_review(
        review_input=review_input,
        agent=FakeQualityAgent(),
    )

    assert len(findings) == 1
    assert findings[0].file_path == "app/main.py"