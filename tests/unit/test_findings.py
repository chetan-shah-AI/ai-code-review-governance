from app.schemas.findings import Finding, Severity, SourceType


def test_create_finding():
    finding = Finding(
        file_path="app/main.py",
        line_number=10,
        severity=Severity.LOW,
        category="lint",
        title="Unused import",
        description="Unused import detected",
        recommendation="Remove the unused import.",
        source_type=SourceType.DETERMINISTIC,
        tool_name="ruff",
    )

    assert finding.file_path == "app/main.py"
    assert finding.line_number == 10
    assert finding.severity == Severity.LOW
    assert finding.source_type == SourceType.DETERMINISTIC