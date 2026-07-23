import re

from app.schemas.findings import Finding, Severity, SourceType, ToolResult
from app.tools.command_runner import run_command


MYPY_PATTERN = re.compile(r"^(.*?):(\d+):\s*(error|note):\s*(.*)$")


def run_mypy(target_path: str = "app") -> ToolResult:
    """
    Run MyPy and convert type errors into Finding objects.
    """

    success, output = run_command(
        ["mypy", target_path],
        timeout_seconds=60,
    )

    findings: list[Finding] = []

    for line in output.splitlines():
        match = MYPY_PATTERN.match(line)

        if not match:
            continue

        file_path, line_number, message_type, message = match.groups()

        if message_type == "note":
            severity = Severity.INFO
        else:
            severity = Severity.MEDIUM

        findings.append(
            Finding(
                file_path=file_path,
                line_number=int(line_number),
                severity=severity,
                category="type_checking",
                title="MyPy type issue",
                description=message,
                recommendation="Fix the typing issue reported by MyPy.",
                source_type=SourceType.DETERMINISTIC,
                tool_name="mypy",
            )
        )

    return ToolResult(
        tool_name="mypy",
        success=success,
        raw_output=output,
        findings=findings,
    )