from fastapi import APIRouter, Request, Header, HTTPException
from app.core.config import settings
from app.core.security import verify_github_signature
from app.clients.github_client import GitHubClient
from app.utils.file_filters import classify_files
from app.services.review_input_service import build_review_input


router = APIRouter()

@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(default=None),
    x_github_event: str = Header(default=None)
):
    payload = await request.body()

    if not verify_github_signature(
        payload,
        x_hub_signature_256,
        settings.github_webhook_secret
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )

    data = await request.json()

    if x_github_event != "pull_request":
        return {"status": "ignored"}


    github_client = GitHubClient()

    repo = data["repository"]["full_name"]
    pr_number = data["pull_request"]["number"]

    pr_details = await github_client.get_pull_request(
        repo,
        pr_number
    )

    files = await github_client.get_pull_request_files(
        repo,
        pr_number
    )

    classified = classify_files(files)


    for f in files:
        print(f"File: {f['filename']}, Additions: {f['additions']}, Deletions: {f['deletions']}")
        # print(f"Patch: {f.get('patch', 'No patch available')}")

    review_input = build_review_input(
        repo_full_name=repo,
        pr_number=pr_number,
        raw_pr=pr_details,
        raw_files=files,
    )
    print(f"Built review input for PR #{pr_number} in {repo} with {len(review_input.files)} files to review.")
    
    return {
        "status": "accepted",
        "repo": repo,
        "pr_number": pr_number,
        "title": pr_details.get("title"),
        "changed_files_count": len(files),
        "review_input": review_input.model_dump(),
            
    
        "summary": {
            "source_files": len(classified["source"]),
            "test_files": len(classified["tests"]),
            "config_files": len(classified["config"]),
            "docs": len(classified["docs"]),
            "infra": len(classified["infra"]),
            "ignored": len(classified["ignored"]),
        },

        "classified_files": classified

    }