from app.schemas.findings import Finding, Severity, SourceType
from app.schemas.review import ReviewInput
from app.services.policy_service import PolicyService


class GovernanceAgent:
    """
    Governance review agent.
    Reviews diff chunks against governance/security policy rules.
    """

    def review(self, review_input: ReviewInput) -> list[Finding]:
        policy_service = PolicyService()
        policies = policy_service.load_policies()

        print("\nLoaded Policies")
        for name in policies:
            print(f"- {name}")

        findings: list[Finding] = []

        for review_file in review_input.files:
            for chunk in review_file.chunks:
                content = chunk.content.lower()

                if "password" in content:
                    findings.append(
                        Finding(
                            file_path=review_file.filename,
                            line_number=chunk.start_line,
                            severity=Severity.HIGH,
                            category="governance",
                            title="Possible hardcoded password",
                            description="Possible hardcoded password detected.",
                            recommendation="Move secrets to environment variables.",
                            source_type=SourceType.GOVERNANCE,
                            tool_name="governance_agent",
                            confidence=0.95,
                        )
                    )

                if "eval(" in content:
                    findings.append(
                        Finding(
                            file_path=review_file.filename,
                            line_number=chunk.start_line,
                            severity=Severity.HIGH,
                            category="security",
                            title="Unsafe eval() usage",
                            description="Use of eval() detected.",
                            recommendation="Avoid eval(); use safer parsing or validation.",
                            source_type=SourceType.GOVERNANCE,
                            tool_name="governance_agent",
                            confidence=0.95,
                        )
                    )

        return findings