# from app.graph.workflow import build_review_workflow

# from app.schemas.review import (
#     ReviewInput,
#     ReviewFile,
#     FileChunk,
# )

# review = ReviewInput(
#     repository="demo",
#     pr_number=1,
#     author="chetan",
#     commit_sha="abc123",
#     files=[
#         ReviewFile(
#             filename="app/main.py",
#             file_type="source",
#             language="python",
#             status="modified",
#             additions=5,
#             deletions=1,
#             patch="""
# + password = "admin123"
# + eval(user_input)
# """,
#             chunks=[
#                 FileChunk(
#                     chunk_index=1,
#                     start_line=1,
#                     end_line=2,
#                     content="""
# + password = "admin123"
# + eval(user_input)
# """
#                 )
#             ]
#         )
#     ]
# )

# password = "admin123"

# eval(user_input)


# workflow = build_review_workflow()

# result = workflow.invoke(
#     {
#         "review_input": review
#     }
# )

# print()

# print("=" * 60)
# print("GOVERNANCE FINDINGS")
# print("=" * 60)

# for finding in result["governance_findings"]:

#     print(finding)


# print()

# print("=" * 60)
# print("ALL FINDINGS")
# print("=" * 60)

# for finding in result["all_findings"]:

#     print(finding.title)


# print()

# print("=" * 60)
# print("VERDICT")
# print("=" * 60)

# print(result["verdict"])


# print()

# print("=" * 60)
# print("SUMMARY")
# print("=" * 60)

# print(result["summary"])


# assert len(result["governance_findings"]) > 0



# assert len(result["all_findings"]) >= len(result["governance_findings"])


# assert result["verdict"] is not None


# assert result["summary"] != ""
from app.graph.workflow import build_review_workflow
from app.schemas.review import ReviewFileInput, ReviewInput, DiffChunk


def test_week7_governance_workflow():
    review = ReviewInput(
        repo_full_name="demo/repo",
        pr_number=1,
        title="Add insecure authentication logic",
        author="chetan",
        commit_sha="abc123",
        files=[
            ReviewFileInput(
                filename="app/main.py",
                file_type="source",
                status="modified",
                additions=2,
                deletions=0,
                chunks=[
                    DiffChunk(
                        file_path="app/main.py",
                        chunk_index=1,
                        start_line=1,
                        end_line=2,
                        content="""
+ password = "admin123"
+ eval(user_input)
""".strip(),
                    )
                ],
            )
        ],
    )

    workflow = build_review_workflow()

    result = workflow.invoke(
        {
            "review_input": review,
        }
    )

    print("\n========== GOVERNANCE FINDINGS ==========")
    for finding in result["governance_findings"]:
        print(finding)

    print("\n========== ALL FINDINGS ==========")
    for finding in result["all_findings"]:
        print(finding.title)

    print("\n========== VERDICT ==========")
    print(result["verdict"])

    print("\n========== SUMMARY ==========")
    print(result["summary"])

    assert len(result["governance_findings"]) > 0
    assert len(result["all_findings"]) >= len(result["governance_findings"])
    assert result["verdict"] is not None
    assert result["summary"] != ""