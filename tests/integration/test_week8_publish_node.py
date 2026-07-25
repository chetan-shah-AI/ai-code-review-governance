from unittest.mock import patch

from app.graph.nodes import publish_review_node
from app.schemas.review import (
    DiffChunk,
    ReviewFileInput,
    ReviewInput,
)


@patch(
    "app.graph.nodes.GitHubClient"
)
def test_week8_publish_node(
    mock_github_client_class,
):
    mock_github_client = (
        mock_github_client_class.return_value
    )

    mock_github_client.create_or_update_review_comment.return_value = {
        "id": 999,
        "html_url": (
            "https://github.com/demo/repo/"
            "pull/1#issuecomment-999"
        ),
    }

    review = ReviewInput(
        repo_full_name="demo/repo",
        pr_number=1,
        title="Add authentication logic",
        author="chetan",
        commit_sha="abc123",
        files=[
            ReviewFileInput(
                filename="app/main.py",
                file_type="source",
                status="modified",
                additions=2,
                deletions=0,
                chunks=[
                    DiffChunk(
                        file_path="app/main.py",
                        chunk_index=1,
                        start_line=1,
                        end_line=2,
                        content=(
                            '+ password = "admin123"\n'
                            "+ eval(user_input)"
                        ),
                    )
                ],
            )
        ],
    )

    state = {
        "review_input": review,
        "verdict": "CHANGES_REQUESTED",
        "summary": (
            "Security concerns were identified."
        ),
        "all_findings": [
            {
                "file_path": "app/main.py",
                "line_number": 1,
                "severity": "high",
                "category": "security",
                "title": "Hardcoded password",
                "description": (
                    "A hardcoded password was found."
                ),
                "recommendation": (
                    "Use an environment variable."
                ),
                "source_type": "governance",
                "tool_name": "governance_agent",
                "confidence": 0.95,
            }
        ],
        "publish_enabled": True,
    }

    with patch(
        "app.graph.nodes.settings.github_token",
        "test-token",
    ):
        result = publish_review_node(state)

    assert result["publish_result"][
        "success"
    ] is True

    assert result["publish_result"][
        "status"
    ] == "published"

    assert result["publish_result"][
        "comment_id"
    ] == 999

    assert (
        "# 🤖 AI Code Review"
        in result["publish_markdown"]
    )

    mock_github_client.create_or_update_review_comment.assert_called_once()

    call_arguments = (
        mock_github_client
        .create_or_update_review_comment
        .call_args
    )

    assert (
        call_arguments.kwargs["repo_full_name"]
        == "demo/repo"
    )

    assert (
        call_arguments.kwargs["pr_number"]
        == 1
    )