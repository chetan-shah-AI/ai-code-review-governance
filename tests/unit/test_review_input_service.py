from app.services.review_input_service import build_review_input


def test_build_review_input_filters_and_chunks_files():
    raw_pr = {
        "title": "Add user service",
        "user": {"login": "raja"},
        "head": {"sha": "abc123"},
    }

    raw_files = [
        {
            "filename": "app/services/user_service.py",
            "status": "modified",
            "additions": 10,
            "deletions": 2,
            "patch": """@@ -1,3 +1,4 @@
 def create_user():
+    validate_user()
     return True
""",
        },
        {
            "filename": "package-lock.json",
            "status": "modified",
            "additions": 500,
            "deletions": 200,
            "patch": "large generated content",
        },
    ]

    review_input = build_review_input(
        repo_full_name="raja/example-repo",
        pr_number=12,
        raw_pr=raw_pr,
        raw_files=raw_files,
    )

    assert review_input.repo_full_name == "raja/example-repo"
    assert review_input.pr_number == 12
    assert review_input.title == "Add user service"
    assert review_input.author == "raja"
    assert review_input.commit_sha == "abc123"

    assert len(review_input.files) == 1
    assert review_input.files[0].filename == "app/services/user_service.py"
    assert review_input.files[0].file_type == "source"
    assert len(review_input.files[0].chunks) == 1