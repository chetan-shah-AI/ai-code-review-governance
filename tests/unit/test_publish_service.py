from app.services.publish_service import (
    PublishService,
)


def test_build_comment_with_findings():
    service = PublishService()

    findings = [
        {
            "file_path": "app/main.py",
            "line_number": 10,
            "severity": "high",
            "category": "security",
            "title": "Hardcoded password",
            "description": (
                "A password appears to be "
                "hardcoded in the source code."
            ),
            "recommendation": (
                "Move the secret to an "
                "environment variable."
            ),
            "source_type": "governance",
            "tool_name": "governance_agent",
            "confidence": 0.95,
        },
        {
            "file_path": "app/main.py",
            "line_number": 15,
            "severity": "medium",
            "category": "quality",
            "title": "Unsafe eval usage",
            "description": (
                "The code calls eval()."
            ),
            "recommendation": (
                "Use a safer parser."
            ),
            "source_type": "governance",
            "tool_name": "governance_agent",
            "confidence": 0.90,
        },
    ]

    comment = service.build_comment(
        verdict="CHANGES_REQUESTED",
        summary=(
            "The Pull Request contains "
            "security issues."
        ),
        findings=findings,
    )

    assert "# 🤖 AI Code Review" in comment
    assert "CHANGES_REQUESTED" in comment
    assert "Hardcoded password" in comment
    assert "Unsafe eval usage" in comment
    assert "`app/main.py`, line `10`" in comment
    assert "95%" in comment
    assert (
        "ai-code-review-governance-comment"
        in comment
    )


def test_build_comment_without_findings():
    service = PublishService()

    comment = service.build_comment(
        verdict="APPROVED",
        summary="No issues were identified.",
        findings=[],
    )

    assert "APPROVED" in comment
    assert (
        "No review findings were identified."
        in comment
    )


def test_build_comment_accepts_dictionary_summary():
    service = PublishService()

    comment = service.build_comment(
        verdict="COMMENT",
        summary={
            "summary": (
                "Dictionary summary content."
            )
        },
        findings=[],
    )

    assert (
        "Dictionary summary content."
        in comment
    )