from collections import Counter

from app.graph.state import ReviewGraphState
from app.schemas.findings import Finding
from app.services.ai_review_service import run_ai_quality_review
from app.services.deterministic_review_service import run_deterministic_review_for_input
from app.services.verdict_service import calculate_verdict
from app.agents.governance_agent import GovernanceAgent

import asyncio

from app.services.publish_service import publish_review_to_github


# from app.schemas.review import DiffChunk, ReviewFileInput, ReviewInput

# def temporary_run(review_input): 
    

#     file_types = [file.file_type for file in review_input.files]
#     file_type_counts = dict(Counter(file_types))

#     total_files = len(review_input.files)
#     total_chunks = sum(len(file.chunks) for file in review_input.files)

#     print(f"Triage summary: {total_files} files, {total_chunks} chunks, file types: {file_type_counts}")

#     return {
#         "triage_summary": {
#             "total_files": total_files,
#             "total_chunks": total_chunks,
#             "file_type_counts": file_type_counts,
#         },
#     }

# review_input = ReviewInput(
#     repo_full_name="local/demo",
#     pr_number=1,
#     title="Demo AI review",
#     author="local",
#     commit_sha="abc123",
#     files=[
#         ReviewFileInput(
#             filename="app/demo.py",
#             file_type="source",
#             status="modified",
#             additions=4,
#             deletions=0,
#             chunks=[
#                 DiffChunk(
#                     file_path="app/demo.py",
#                     chunk_index=0,
#                     start_line=1,
#                     end_line=5,
#                     content=(
#                         "@@ -1,2 +1,5 @@\n"
#                         "+def get_user(id):\n"
#                         "+    query = \"SELECT * FROM users WHERE id = \" + id\n"
#                         "+    return db.execute(query)\n"
#                     ),
#                 )
#             ],
#         )
#     ],
# )

# temporary_run(review_input)


def triage_node(state: ReviewGraphState) -> ReviewGraphState:
    """
    Understand what kind of PR this is.
    """

    review_input = state["review_input"]

    print(f"Triage: PR #{review_input.pr_number} in {review_input.repo_full_name}")

    file_types = [file.file_type for file in review_input.files]
    file_type_counts = dict(Counter(file_types))

    total_files = len(review_input.files)
    print(f"Triage summary: {total_files} files, file types: {file_type_counts}")
    total_chunks = sum(len(file.chunks) for file in review_input.files)

    return {
        **state,
        "triage_summary": {
            "total_files": total_files,
            "total_chunks": total_chunks,
            "file_type_counts": file_type_counts,
        },
    }




def deterministic_review_node(state: ReviewGraphState) -> ReviewGraphState:
    """
    Run deterministic tools such as Ruff, MyPy, Bandit, and Pytest.
    """

    try:
        tool_results, findings = run_deterministic_review_for_input(
                state["review_input"]
                                    )

        return {
            **state,
            "deterministic_tool_results": tool_results,
            "deterministic_findings": findings,
        }

    except Exception as error:
        errors = state.get("errors", [])
        errors.append(f"Deterministic review failed: {str(error)}")

        return {
            **state,
            "deterministic_tool_results": [],
            "deterministic_findings": [],
            "errors": errors,
        }


def ai_review_node(state: ReviewGraphState) -> ReviewGraphState:
    """
    Run AI quality review on source and test files.
    """

    review_input = state["review_input"]

    try:
        findings = run_ai_quality_review(review_input)

        return {
            **state,
            "ai_findings": findings,
        }

    except Exception as error:
        errors = state.get("errors", [])
        errors.append(f"AI review failed: {str(error)}")

        return {
            **state,
            "ai_findings": [],
            "errors": errors,
        }


def merge_findings_node(state: ReviewGraphState) -> ReviewGraphState:
    """
    Merge deterministic, AI, and governance findings
    into a single list.
    """

    deterministic_findings = state.get(
        "deterministic_findings",
        [],
    )

    ai_findings = state.get(
        "ai_findings",
        [],
    )

    governance_findings = state.get(
        "governance_findings",
        [],
    )

    all_findings: list[Finding] = [
        *deterministic_findings,
        *ai_findings,
        *governance_findings,
    ]

    return {
        **state,
        "all_findings": all_findings,
    }


def verdict_node(state: ReviewGraphState) -> ReviewGraphState:
    """
    Calculate the final verdict.
    """

    all_findings = state.get("all_findings", [])
    verdict = calculate_verdict(all_findings)

    return {
        **state,
        "verdict": verdict,
    }


def summary_node(state: ReviewGraphState) -> ReviewGraphState:
    """
    Create a simple human-readable review summary.
    """

    review_input = state["review_input"]
    all_findings = state.get("all_findings", [])
    verdict = state.get("verdict")
    triage_summary = state.get("triage_summary", {})
    errors = state.get("errors", [])

    severity_counts = Counter(finding.severity.value for finding in all_findings)

    summary_lines = [
        f"AI Code Review Summary for PR #{review_input.pr_number}",
        "",
        f"Repository: {review_input.repo_full_name}",
        f"Title: {review_input.title}",
        f"Verdict: {verdict}",
        "",
        "Triage:",
        f"- Files reviewed: {triage_summary.get('total_files', 0)}",
        f"- Diff chunks: {triage_summary.get('total_chunks', 0)}",
        f"- File types: {triage_summary.get('file_type_counts', {})}",
        "",
        "Findings:",
        f"- Total findings: {len(all_findings)}",
        f"- Severity counts: {dict(severity_counts)}",
    ]

    if errors:
        summary_lines.append("")
        summary_lines.append("Errors:")
        for error in errors:
            summary_lines.append(f"- {error}")

    if all_findings:
        summary_lines.append("")
        summary_lines.append("Top Findings:")

        for finding in all_findings[:5]:
            summary_lines.append(
                f"- [{finding.severity.value}] {finding.title} "
                f"({finding.file_path}:{finding.line_number})"
            )

    return {
        **state,
        "summary": "\n".join(summary_lines),
    }

def governance_review_node(
    state: ReviewGraphState,
) -> ReviewGraphState:

    agent = GovernanceAgent()

    findings = agent.review(
        state["review_input"]
    )

    state["governance_findings"] = findings

    return state


def publish_node(state: ReviewGraphState) -> ReviewGraphState:
    """
    Publish the final review summary to GitHub.
    """

    try:
        publish_result = asyncio.run(
            publish_review_to_github(state)
        )

        return {
            **state,
            "publish_result": publish_result,
        }

    except Exception as error:
        errors = state.get("errors", [])
        errors.append(f"GitHub publishing failed: {str(error)}")

        return {
            **state,
            "errors": errors,
        }