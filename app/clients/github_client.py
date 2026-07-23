import httpx

from app.core.config import settings


class GitHubClient:
    """
    Client for interacting with GitHub API.
    """

    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_pull_request(self, repo_full_name: str, pr_number: int):
        url = f"{self.base_url}/repos/{repo_full_name}/pulls/{pr_number}"

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_pull_request_files(self, repo_full_name: str, pr_number: int):
        url = f"{self.base_url}/repos/{repo_full_name}/pulls/{pr_number}/files"

        all_files = []
        page = 1

        async with httpx.AsyncClient(timeout=20) as client:
            while True:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params={"page": page, "per_page": 100},
                )
                response.raise_for_status()

                files = response.json()

                if not files:
                    break

                all_files.extend(files)
                page += 1

        return all_files

    async def list_issue_comments(
        self,
        repo_full_name: str,
        pr_number: int,
    ) -> list[dict]:
        """
        GitHub PR comments use the issues comments API.
        """

        url = f"{self.base_url}/repos/{repo_full_name}/issues/{pr_number}/comments"

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def create_issue_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        body: str,
    ) -> dict:
        """
        Create a new PR comment.
        """

        url = f"{self.base_url}/repos/{repo_full_name}/issues/{pr_number}/comments"

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json={"body": body},
            )
            response.raise_for_status()
            return response.json()

    async def update_issue_comment(
        self,
        repo_full_name: str,
        comment_id: int,
        body: str,
    ) -> dict:
        """
        Update an existing PR comment.
        """

        url = f"{self.base_url}/repos/{repo_full_name}/issues/comments/{comment_id}"

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.patch(
                url,
                headers=self.headers,
                json={"body": body},
            )
            response.raise_for_status()
            return response.json()