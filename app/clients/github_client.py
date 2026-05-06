import httpx
from app.core.config import settings

class GitHubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json"
        }

    async def get_pull_request(self, repo: str, pr_number: int):
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=self.headers)
            res.raise_for_status()
            return res.json()

    async def get_pull_request_files(self, repo: str, pr_number: int):
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/files"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=self.headers)
            res.raise_for_status()
            return res.json()