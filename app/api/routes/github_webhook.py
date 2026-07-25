import json
from typing import Any

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Request,
    status,
)

from app.clients.github_client import (
    GitHubClient,
    GitHubClientError,
)
from app.core.config import settings
from app.graph.workflow import build_review_workflow
from app.services.github_review_input_service import (
    build_review_input,
)
from app.services.github_webhook_service import (
    GitHubWebhookValidationError,
    verify_github_signature,
)


router = APIRouter(
    prefix="/github",
    tags=["GitHub"],
)

workflow = build_review_workflow()


@router.post("/webhook")
async def github_webhook(
    request: Request,
    x_github_event: str | None = Header(
        default=None,
        alias="X-GitHub-Event",
    ),
    x_github_delivery: str | None = Header(
        default=None,
        alias="X-GitHub-Delivery",
    ),
    x_hub_signature_256: str | None = Header(
        default=None,
        alias="X-Hub-Signature-256",
    ),
) -> dict[str, Any]:
    """
    Receive GitHub Pull Request events, run the
    AI review workflow and publish the result.
    """

    raw_body = await request.body()

    if not settings.github_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "GITHUB_WEBHOOK_SECRET is not configured."
            ),
        )

    try:
        verify_github_signature(
            payload_body=raw_body,
            signature_header=x_hub_signature_256,
            webhook_secret=(
                settings.github_webhook_secret
            ),
        )

    except GitHubWebhookValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    try:
        payload = json.loads(raw_body)

    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook body is not valid JSON.",
        ) from exc

    if x_github_event == "ping":
        return {
            "status": "ok",
            "message": "GitHub webhook connected.",
            "delivery_id": x_github_delivery,
        }

    if x_github_event != "pull_request":
        return {
            "status": "ignored",
            "reason": (
                f"Unsupported event: {x_github_event}"
            ),
            "delivery_id": x_github_delivery,
        }

    action = payload.get("action")

    supported_actions = {
        "opened",
        "reopened",
        "synchronize",
        "ready_for_review",
    }

    if action not in supported_actions:
        return {
            "status": "ignored",
            "reason": (
                f"Unsupported pull request action: {action}"
            ),
            "delivery_id": x_github_delivery,
        }

    pull_request_payload = payload.get(
        "pull_request",
        {},
    )

    repository = payload.get(
        "repository",
        {},
    ).get(
        "full_name"
    )

    pr_number = payload.get("number")

    if not repository or pr_number is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Repository or Pull Request number "
                "is missing from the webhook."
            ),
        )

    if not settings.github_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GITHUB_TOKEN is not configured.",
        )

    github_client = GitHubClient(
        token=settings.github_token,
        base_url=settings.github_api_url,
    )

    try:
        pull_request = (
            await github_client.get_pull_request(
                repo_full_name=repository,
                pr_number=int(pr_number),
            )
        )

        changed_files = (
            await github_client.get_pull_request_files(
                repo_full_name=repository,
                pr_number=int(pr_number),
            )
        )

    except GitHubClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    review_input = build_review_input(
        pull_request=pull_request,
        changed_files=changed_files,
    )

    try:
        result = await workflow.ainvoke(
            {
                "review_input": review_input,
                "publish_enabled": True,
            }
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"AI review workflow failed: {exc}"
            ),
        ) from exc

    publish_result = result.get(
        "publish_result",
        {},
    )

    return {
        "status": "completed",
        "delivery_id": x_github_delivery,
        "repository": repository,
        "pr_number": pr_number,
        "verdict": str(
            result.get(
                "verdict",
                "UNKNOWN",
            )
        ),
        "findings_count": len(
            result.get(
                "all_findings",
                [],
            )
        ),
        "publish_result": publish_result,
    }