from typing import Any

import httpx

from app.core.config import settings


class GitHubClientError(Exception):
    """
    Raised when a GitHub API request fails.
    """


class GitHubClient:
    """
    Client for interacting with the GitHub REST API.
    """

    def __init__(
        self,
        token: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float = 20.0,
    ):
        self.token = token or settings.github_token

        self.base_url = (
            base_url
            or getattr(
                settings,
                "github_api_url",
                "https://api.github.com",
            )
        ).rstrip("/")

        self.timeout_seconds = timeout_seconds

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ai-code-review-governance",
        }

    async def get_pull_request(
        self,
        repo_full_name: str,
        pr_number: int,
    ) -> dict[str, Any]:
        """
        Fetch Pull Request metadata.
        """

        endpoint = (
            f"/repos/{repo_full_name}"
            f"/pulls/{pr_number}"
        )

        return await self._async_request(
            method="GET",
            endpoint=endpoint,
        )

    async def get_pull_request_files(
        self,
        repo_full_name: str,
        pr_number: int,
    ) -> list[dict[str, Any]]:
        """
        Fetch all changed files for a Pull Request.
        """

        endpoint = (
            f"/repos/{repo_full_name}"
            f"/pulls/{pr_number}/files"
        )

        all_files: list[dict[str, Any]] = []
        page = 1

        while True:
            response = await self._async_request(
                method="GET",
                endpoint=endpoint,
                params={
                    "page": page,
                    "per_page": 100,
                },
            )

            if not isinstance(response, list):
                raise GitHubClientError(
                    "GitHub files response was not a list."
                )

            if not response:
                break

            all_files.extend(response)

            if len(response) < 100:
                break

            page += 1

        return all_files

    def create_pr_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        body: str,
    ) -> dict[str, Any]:
        """
        Create a general Pull Request comment.
        """

        if not body.strip():
            raise ValueError(
                "GitHub comment body cannot be empty."
            )

        endpoint = (
            f"/repos/{repo_full_name}"
            f"/issues/{pr_number}/comments"
        )

        response = self._request(
            method="POST",
            endpoint=endpoint,
            json={
                "body": body,
            },
        )

        if not isinstance(response, dict):
            raise GitHubClientError(
                "GitHub comment response was not an object."
            )

        return response

    def update_pr_comment(
        self,
        repo_full_name: str,
        comment_id: int,
        body: str,
    ) -> dict[str, Any]:
        """
        Update an existing Pull Request comment.
        """

        if not body.strip():
            raise ValueError(
                "GitHub comment body cannot be empty."
            )

        endpoint = (
            f"/repos/{repo_full_name}"
            f"/issues/comments/{comment_id}"
        )

        response = self._request(
            method="PATCH",
            endpoint=endpoint,
            json={
                "body": body,
            },
        )

        if not isinstance(response, dict):
            raise GitHubClientError(
                "GitHub update response was not an object."
            )

        return response

    def list_pr_comments(
        self,
        repo_full_name: str,
        pr_number: int,
    ) -> list[dict[str, Any]]:
        """
        List existing Pull Request comments.
        """

        endpoint = (
            f"/repos/{repo_full_name}"
            f"/issues/{pr_number}/comments"
        )

        response = self._request(
            method="GET",
            endpoint=endpoint,
            params={
                "per_page": 100,
            },
        )

        if not isinstance(response, list):
            raise GitHubClientError(
                "GitHub comments response was not a list."
            )

        return response

    def create_or_update_review_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        body: str,
        marker: str = (
            "ai-code-review-governance-comment"
        ),
    ) -> dict[str, Any]:
        """
        Update the previous bot comment instead of
        creating duplicate review comments.
        """

        comments = self.list_pr_comments(
            repo_full_name=repo_full_name,
            pr_number=pr_number,
        )

        for comment in comments:
            comment_body = str(
                comment.get(
                    "body",
                    "",
                )
            )

            if marker not in comment_body:
                continue

            comment_id = comment.get("id")

            if comment_id is None:
                continue

            return self.update_pr_comment(
                repo_full_name=repo_full_name,
                comment_id=int(comment_id),
                body=body,
            )

        return self.create_pr_comment(
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            body=body,
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute a synchronous GitHub REST request.
        """

        url = f"{self.base_url}{endpoint}"

        try:
            with httpx.Client(
                timeout=self.timeout_seconds,
            ) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=json,
                    params=params,
                )

        except httpx.HTTPError as exc:
            raise GitHubClientError(
                f"Unable to connect to GitHub: {exc}"
            ) from exc

        return self._handle_response(response)

    async def _async_request(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute an asynchronous GitHub REST request.
        """

        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds,
            ) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=json,
                    params=params,
                )

        except httpx.HTTPError as exc:
            raise GitHubClientError(
                f"Unable to connect to GitHub: {exc}"
            ) from exc

        return self._handle_response(response)

    def _handle_response(
        self,
        response: httpx.Response,
    ) -> Any:
        """
        Validate and decode a GitHub API response.
        """

        if response.status_code >= 400:
            try:
                error_body = response.json()
            except ValueError:
                error_body = response.text

            raise GitHubClientError(
                (
                    "GitHub API request failed. "
                    f"Status: {response.status_code}. "
                    f"Response: {error_body}"
                )
            )

        if response.status_code == 204:
            return {}

        try:
            return response.json()

        except ValueError as exc:
            raise GitHubClientError(
                "GitHub returned invalid JSON."
            ) from exc