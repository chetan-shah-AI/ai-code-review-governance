from app.schemas.findings import Finding, Severity, SourceType, ToolResult
from app.services import run_deterministic_review_for_input


def fake_tool_result(tool_name: str) -> ToolResult:
    return ToolResult(
        tool_name=tool_name,
        success=True,
        raw_output="",
        findings=[
            Finding(
                file_path="app/main.py",
                line_number=1,
                severity=Severity.LOW,
                category="test",
                title=f"{tool_name} finding",
                description="fake finding",
                recommendation="fix it",
                source_type=SourceType.DETERMINISTIC,
                tool_name=tool_name,
            )
        ],
    )


def test_run_deterministic_review_combines_findings(monkeypatch):
    monkeypatch.setattr(
        run_deterministic_review_for_input,
        "run_ruff",
        lambda target_path: fake_tool_result("ruff"),
    )

    monkeypatch.setattr(
        run_deterministic_review_for_input,
        "run_mypy",
        lambda target_path: fake_tool_result("mypy"),
    )

    monkeypatch.setattr(
        run_deterministic_review_for_input,
        "run_bandit",
        lambda target_path: fake_tool_result("bandit"),
    )

    monkeypatch.setattr(
        run_deterministic_review_for_input,
        "run_pytest",
        lambda target_path: fake_tool_result("pytest"),
    )

    tool_results, findings = run_deterministic_review_for_input.run_deterministic_review(".")

    assert len(tool_results) == 4
    assert len(findings) == 4

    tool_names = [finding.tool_name for finding in findings]

    assert "ruff" in tool_names
    assert "mypy" in tool_names
    assert "bandit" in tool_names
    assert "pytest" in tool_names