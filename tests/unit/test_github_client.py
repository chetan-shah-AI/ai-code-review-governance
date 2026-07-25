from unittest.mock import Mock, patch

from app.clients.github_client import (
    GitHubClient,
)


@patch("app.clients.github_client.httpx.Client")
def test_create_pr_comment(
    mock_client_class,
):
    mock_response = Mock()

    mock_response.status_code = 201

    mock_response.json.return_value = {
        "id": 12345,
        "html_url": (
            "https://github.com/demo/repo/"
            "pull/1#issuecomment-12345"
        ),
    }

    mock_http_client = Mock()

    mock_http_client.request.return_value = (
        mock_response
    )

    mock_client_class.return_value.__enter__.return_value = (
        mock_http_client
    )

    client = GitHubClient(
        token="test-token",
    )

    result = client.create_pr_comment(
        repo_full_name="demo/repo",
        pr_number=1,
        body="Test review comment",
    )

    assert result["id"] == 12345

    mock_http_client.request.assert_called_once()

    call_arguments = (
        mock_http_client.request.call_args
    )

    assert call_arguments.kwargs["method"] == "POST"

    assert (
        call_arguments.kwargs["url"]
        == (
            "https://api.github.com"
            "/repos/demo/repo"
            "/issues/1/comments"
        )
    )

    assert call_arguments.kwargs["json"] == {
        "body": "Test review comment"
    }