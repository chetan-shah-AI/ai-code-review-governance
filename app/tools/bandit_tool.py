import json

from app.schemas.findings import Finding, Severity, SourceType, ToolResult
from app.tools.command_runner import run_command


def map_bandit_severity(severity: str) -> Severity:
    severity = severity.upper()

    if severity == "LOW":
        return Severity.LOW

    if severity == "MEDIUM":
        return Severity.MEDIUM

    if severity == "HIGH":
        return Severity.HIGH

    return Severity.INFO


def run_bandit(target_path: str = "app") -> ToolResult:
    """
    Run Bandit and convert security findings into Finding objects.
    """

    success, output = run_command(
        ["bandit", "-r", target_path, "-f", "json"],
        timeout_seconds=60,
    )

    findings: list[Finding] = []

    if output:
        try:
            data = json.loads(output)
            results = data.get("results", [])

            for issue in results:
                findings.append(
                    Finding(
                        file_path=issue.get("filename"),
                        line_number=issue.get("line_number"),
                        severity=map_bandit_severity(issue.get("issue_severity", "LOW")),
                        category="security",
                        title=issue.get("test_name", "Bandit security issue"),
                        description=issue.get("issue_text", "Bandit detected a security issue"),
                        recommendation="Review and fix the security issue reported by Bandit.",
                        source_type=SourceType.DETERMINISTIC,
                        tool_name="bandit",
                        confidence=0.9,
                    )
                )

        except json.JSONDecodeError:
            findings.append(
                Finding(
                    severity=Severity.MEDIUM,
                    category="tool_error",
                    title="Bandit output parsing failed",
                    description=output,
                    recommendation="Check Bandit output format.",
                    source_type=SourceType.DETERMINISTIC,
                    tool_name="bandit",
                )
            )

    return ToolResult(
        tool_name="bandit",
        success=success,
        raw_output=output,
        findings=findings,
    )