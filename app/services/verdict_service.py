from enum import Enum

from app.schemas.findings import Finding, Severity


class Verdict(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


def calculate_verdict(findings: list[Finding]) -> Verdict:
    """
    Calculate the final PR verdict from all findings.
    """

    severities = [finding.severity for finding in findings]

    if Severity.CRITICAL in severities:
        return Verdict.ESCALATE_TO_HUMAN

    if Severity.HIGH in severities:
        return Verdict.CHANGES_REQUESTED

    if Severity.MEDIUM in severities:
        return Verdict.PASS_WITH_WARNINGS

    return Verdict.PASS