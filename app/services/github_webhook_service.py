import hashlib
import hmac


class GitHubWebhookValidationError(Exception):
    """
    Raised when a GitHub webhook signature is invalid.
    """


def verify_github_signature(
    payload_body: bytes,
    signature_header: str | None,
    webhook_secret: str,
) -> None:
    """
    Verify GitHub's X-Hub-Signature-256 header.

    Raises GitHubWebhookValidationError when the
    signature is absent or invalid.
    """

    if not signature_header:
        raise GitHubWebhookValidationError(
            "Missing X-Hub-Signature-256 header."
        )

    if not signature_header.startswith("sha256="):
        raise GitHubWebhookValidationError(
            "Invalid GitHub signature format."
        )

    expected_digest = hmac.new(
        key=webhook_secret.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    expected_signature = f"sha256={expected_digest}"

    if not hmac.compare_digest(
        expected_signature,
        signature_header,
    ):
        raise GitHubWebhookValidationError(
            "Invalid GitHub webhook signature."
        )
    
    