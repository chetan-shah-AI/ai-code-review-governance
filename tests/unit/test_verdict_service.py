from app.schemas.findings import Finding, Severity, SourceType
from app.services.verdict_service import Verdict, calculate_verdict


def make_finding(severity: Severity) -> Finding:
    return Finding(
        file_path="app/main.py",
        line_number=1,
        severity=severity,
        category="test",
        title="Test finding",
        description="Test finding description",
        recommendation="Fix it",
        source_type=SourceType.DETERMINISTIC,
        tool_name="test",
    )


def test_pass_when_no_findings():
    assert calculate_verdict([]) == Verdict.PASS


def test_pass_when_low_findings_only():
    assert calculate_verdict([make_finding(Severity.LOW)]) == Verdict.PASS


def test_pass_with_warnings_when_medium_exists():
    assert calculate_verdict([make_finding(Severity.MEDIUM)]) == Verdict.PASS_WITH_WARNINGS


def test_changes_requested_when_high_exists():
    assert calculate_verdict([make_finding(Severity.HIGH)]) == Verdict.CHANGES_REQUESTED


def test_escalate_when_critical_exists():
    assert calculate_verdict([make_finding(Severity.CRITICAL)]) == Verdict.ESCALATE_TO_HUMAN