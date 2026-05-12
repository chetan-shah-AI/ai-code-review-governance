from app.schemas.review import ReviewInput, ReviewFileInput
from app.services.file_classifier import classify_file, should_ignore_file
from app.services.diff_chunker import chunk_patch


MAX_ADDITIONS = 1800
MAX_DELETIONS = 1800


def should_review_file(file: dict) -> bool:
    filename = file.get("filename", "")
    patch = file.get("patch")
    additions = file.get("additions", 0)
    deletions = file.get("deletions", 0)

    if should_ignore_file(filename):
        return False

    if not patch:
        return False

    if additions > MAX_ADDITIONS or deletions > MAX_DELETIONS:
        return False

    return True


def build_review_input(
    repo_full_name: str,
    pr_number: int,
    raw_pr: dict,
    raw_files: list[dict],
) -> ReviewInput:
    review_files = []

    for file in raw_files:
        print(f"Processing file in build review: {file.get('filename', 'unknown')}")
        if not should_review_file(file):
            continue

        filename = file.get("filename", "")
        file_type = classify_file(filename)
        patch = file.get("patch")

        chunks = chunk_patch(
            file_path=filename,
            patch=patch,
            max_lines=80,
        )

        review_files.append(
            ReviewFileInput(
                filename=filename,
                file_type=file_type,
                status=file.get("status", "unknown"),
                additions=file.get("additions", 0),
                deletions=file.get("deletions", 0),
                chunks=chunks,
            )
        )

    return ReviewInput(
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        title=raw_pr.get("title"),
        author=raw_pr.get("user", {}).get("login"),
        commit_sha=raw_pr.get("head", {}).get("sha"),
        files=review_files,
    )

