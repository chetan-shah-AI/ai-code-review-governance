from app.schemas.findings import Finding, Severity, SourceType, ToolResult
from app.tools.command_runner import run_command


def run_pytest(target_path: str = "tests") -> ToolResult:
    """
    Run Pytest and return a finding if tests fail.
    """

    success, output = run_command(
        ["pytest", target_path, "-q"],
        timeout_seconds=120,
    )

    findings: list[Finding] = []

    if not success:
        findings.append(
            Finding(
                file_path=None,
                line_number=None,
                severity=Severity.HIGH,
                category="tests",
                title="Test suite failed",
                description=output or "Pytest failed.",
                recommendation="Fix failing tests before merging.",
                source_type=SourceType.DETERMINISTIC,
                tool_name="pytest",
            )
        )

    return ToolResult(
        tool_name="pytest",
        success=success,
        raw_output=output,
        findings=findings,
    )