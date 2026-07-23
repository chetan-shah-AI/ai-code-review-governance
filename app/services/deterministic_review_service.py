from pathlib import Path

from app.schemas.findings import Finding, ToolResult
from app.schemas.review import ReviewInput
from app.tools.ruff_tool import run_ruff
from app.tools.mypy_tool import run_mypy
from app.tools.bandit_tool import run_bandit


def get_existing_review_paths(review_input: ReviewInput) -> list[str]:
    paths = []

    for file in review_input.files:
        if file.file_type not in {"source", "test"}:
            continue

        path = Path(file.filename)

        if path.exists():
            paths.append(file.filename)

    return paths


def run_deterministic_review_for_input(
    review_input: ReviewInput,
) -> tuple[list[ToolResult], list[Finding]]:
    target_paths = get_existing_review_paths(review_input)

    if not target_paths:
        return [], []

    tool_results: list[ToolResult] = []

    for path in target_paths:
        tool_results.append(run_ruff(path))

        if path.endswith(".py"):
            tool_results.append(run_mypy(path))
            tool_results.append(run_bandit(path))

    all_findings: list[Finding] = []

    for result in tool_results:
        all_findings.extend(result.findings)

    return tool_results, all_findings