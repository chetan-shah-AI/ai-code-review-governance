import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.workflow import run_review_workflow
from app.schemas.review import DiffChunk, ReviewFileInput, ReviewInput


def main():
    review_input = ReviewInput(
        repo_full_name="local/demo",
        pr_number=19,
        title="Week 6 LangGraph Demo",
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
            ),
            ReviewFileInput(
                filename="app/Readme.md",
                file_type="docs",
                status="modified",
                additions=4,
                deletions=0,
                chunks=[
                    DiffChunk(
                        file_path="app/Readme.md",
                        chunk_index=0,
                        start_line=1,
                        end_line=5,
                        content=(
                            "@@ -1,2 +1,5 @@\n"
                            "+Hello, this is a documentation file.\n"
                            "+It should not be reviewed by the deterministic review tools.\n"
                            "+This is just a test to ensure that the deterministic review tools skip non-source files.\n"
                        ),
                    )
                ],
            )
        ],
    )

    result = run_review_workflow(review_input)

    print(result["summary"])


if __name__ == "__main__":
    main()
    