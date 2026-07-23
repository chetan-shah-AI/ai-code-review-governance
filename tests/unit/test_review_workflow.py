from app.graph import nodes
from app.graph.workflow import run_review_workflow
from app.schemas.findings import Finding, Severity, SourceType, ToolResult
from app.schemas.review import DiffChunk, ReviewFileInput, ReviewInput


def make_review_input() -> ReviewInput:
    return ReviewInput(
        repo_full_name="raja/example",
        pr_number=1,
        title="Test PR",
        author="raja",
        commit_sha="abc123",
        files=[
            ReviewFileInput(
                filename="app/main.py",
                file_type="source",
                status="modified",
                additions=3,
                deletions=0,
                chunks=[
                    DiffChunk(
                        file_path="app/main.py",
                        chunk_index=0,
                        start_line=1,
                        end_line=4,
                        content="+print('hello')",
                    )
                ],
            )
        ],
    )


def fake_deterministic_review(review_input):
    finding = Finding(
        file_path="app/main.py",
        line_number=1,
        severity=Severity.LOW,
        category="lint",
        title="Fake lint finding",
        description="Fake deterministic finding",
        recommendation="Fix fake lint issue",
        source_type=SourceType.DETERMINISTIC,
        tool_name="ruff",
    )

    tool_result = ToolResult(
        tool_name="ruff",
        success=True,
        raw_output="",
        findings=[finding],
    )

    return [tool_result], [finding]


def fake_ai_review(review_input: ReviewInput):
    return [
        Finding(
            file_path="app/main.py",
            line_number=2,
            severity=Severity.MEDIUM,
            category="quality",
            title="Fake AI finding",
            description="Fake AI issue",
            recommendation="Fix fake AI issue",
            source_type=SourceType.AI,
            tool_name="quality_review_agent",
            confidence=0.8,
        )
    ]


def test_review_workflow_combines_findings_and_calculates_verdict(monkeypatch):


    monkeypatch.setattr(
        nodes,
        "run_deterministic_review_for_input",
        fake_deterministic_review,
    )

    monkeypatch.setattr(nodes, "run_ai_quality_review", fake_ai_review)

    result = run_review_workflow(make_review_input())

    assert result["triage_summary"]["total_files"] == 1
    assert len(result["deterministic_findings"]) == 1
    assert len(result["ai_findings"]) == 1
    assert len(result["all_findings"]) == 2
    assert result["verdict"].value == "PASS_WITH_WARNINGS"
    assert "AI Code Review Summary" in result["summary"]