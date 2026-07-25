import hashlib
import hmac

import pytest

from app.services.github_webhook_service import (
    GitHubWebhookValidationError,
    verify_github_signature,
)


def test_valid_github_signature():
    secret = "test-secret"
    payload = b'{"action":"opened"}'

    digest = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    signature = f"sha256={digest}"

    verify_github_signature(
        payload_body=payload,
        signature_header=signature,
        webhook_secret=secret,
    )


def test_invalid_github_signature():
    with pytest.raises(
        GitHubWebhookValidationError
    ):
        verify_github_signature(
            payload_body=b'{"action":"opened"}',
            signature_header="sha256=invalid",
            webhook_secret="test-secret",
        )


def test_missing_github_signature():
    with pytest.raises(
        GitHubWebhookValidationError
    ):
        verify_github_signature(
            payload_body=b'{"action":"opened"}',
            signature_header=None,
            webhook_secret="test-secret",
        )