from app.services.publish_service import (
    PublishService,
)


def main():
    service = PublishService()

    findings = [
        {
            "file_path": "app/main.py",
            "line_number": 1,
            "severity": "high",
            "category": "security",
            "title": "Hardcoded password",
            "description": (
                "A password appears directly "
                "inside the source code."
            ),
            "recommendation": (
                "Store the secret in an "
                "environment variable."
            ),
            "source_type": "governance",
            "tool_name": "governance_agent",
            "confidence": 0.95,
        },
        {
            "file_path": "app/main.py",
            "line_number": 2,
            "severity": "high",
            "category": "security",
            "title": "Unsafe eval usage",
            "description": (
                "The code executes eval()."
            ),
            "recommendation": (
                "Replace eval() with safe parsing."
            ),
            "source_type": "governance",
            "tool_name": "governance_agent",
            "confidence": 0.95,
        },
    ]

    comment = service.build_comment(
        verdict="CHANGES_REQUESTED",
        summary=(
            "The proposed changes contain "
            "security policy violations."
        ),
        findings=findings,
    )

    print()
    print(comment)
    print()


if __name__ == "__main__":
    main()
