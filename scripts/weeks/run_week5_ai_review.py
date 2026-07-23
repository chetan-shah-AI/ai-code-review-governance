import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.schemas.review import ReviewInput, ReviewFileInput, DiffChunk
from app.services.ai_review_service import run_ai_quality_review


def main():
    print("Running REAL OpenAI LLM review")
    print(f"Model: {settings.openai_model}")
    print("-" * 60)

    review_input = ReviewInput(
        repo_full_name="local/demo",
        pr_number=1,
        title="Demo AI review",
        author="local",
        commit_sha="abc123",
        files=[
            ReviewFileInput(
                filename="app/demo.py",
                file_type="source",
                status="modified",
                additions=4,
                deletions=0,
                chunks=[
                    DiffChunk(
                        file_path="app/demo.py",
                        chunk_index=0,
                        start_line=1,
                        end_line=5,
                        content=(
                            "@@ -1,2 +1,5 @@\n"
                            "+def get_user(id):\n"
                            "+    query = \"SELECT * FROM users WHERE id = \" + id\n"
                            "+    return db.execute(query)\n"
                        ),
                    )
                ],
            )
        ],
    )

    findings = run_ai_quality_review(review_input)

    if not findings:
        print("LLM returned no findings.")
        return

    for finding in findings:
        print(f"[{finding.severity}] {finding.file_path}:{finding.line_number}")
        print(f"Title: {finding.title}")
        print(f"Description: {finding.description}")
        print(f"Recommendation: {finding.recommendation}")
        print(f"Confidence: {finding.confidence}")
        print(f"Source: {finding.source_type}")
        print(f"Tool: {finding.tool_name}")
        print("-" * 60)


if __name__ == "__main__":
    main()