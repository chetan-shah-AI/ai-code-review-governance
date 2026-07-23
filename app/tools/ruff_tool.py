import json

from app.schemas.findings import Finding, Severity, SourceType, ToolResult
from app.tools.command_runner import run_command


def run_ruff(target_path: str = ".") -> ToolResult:
    """
    Run Ruff against the project and normalize issues into Finding objects.
    """

    success, output = run_command(
        ["ruff", "check", target_path, "--output-format", "json"],
        timeout_seconds=60,
    )

    findings: list[Finding] = []

    if output:
        try:
            issues = json.loads(output)

            for issue in issues:
                location = issue.get("location", {})

                findings.append(
                    Finding(
                        file_path=issue.get("filename"),
                        line_number=location.get("row"),
                        severity=Severity.LOW,
                        category="lint",
                        title=issue.get("code", "Ruff issue"),
                        description=issue.get("message", "Ruff detected an issue"),
                        recommendation="Fix the linting issue reported by Ruff.",
                        source_type=SourceType.DETERMINISTIC,
                        tool_name="ruff",
                    )
                )

        except json.JSONDecodeError:
            findings.append(
                Finding(
                    severity=Severity.MEDIUM,
                    category="tool_error",
                    title="Ruff output parsing failed",
                    description=output,
                    recommendation="Check Ruff output format.",
                    source_type=SourceType.DETERMINISTIC,
                    tool_name="ruff",
                )
            )

    return ToolResult(
        tool_name="ruff",
        success=success,
        raw_output=output,
        findings=findings,
    )