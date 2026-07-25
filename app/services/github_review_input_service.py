from pathlib import Path
from typing import Any

from app.schemas.review import (
    DiffChunk,
    ReviewFileInput,
    ReviewInput,
)


def classify_file(filename: str) -> str:
    """
    Classify a changed file using its extension.
    """

    suffix = Path(filename).suffix.lower()

    source_extensions = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".cs",
        ".go",
        ".rs",
        ".rb",
        ".php",
    }

    test_markers = {
        "test_",
        "_test.",
        ".test.",
        ".spec.",
        "/tests/",
        "/test/",
    }

    configuration_extensions = {
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
    }

    normalised_filename = filename.lower()

    if any(
        marker in normalised_filename
        for marker in test_markers
    ):
        return "test"

    if suffix in source_extensions:
        return "source"

    if suffix in configuration_extensions:
        return "configuration"

    if suffix in {".md", ".rst", ".txt"}:
        return "documentation"

    return "other"


def create_chunks_from_patch(
    filename: str,
    patch: str | None,
    max_lines_per_chunk: int = 100,
) -> list[DiffChunk]:
    """
    Convert a GitHub patch into DiffChunk objects.

    GitHub may omit the patch for binary files or
    exceptionally large diffs.
    """

    if not patch:
        return []

    patch_lines = patch.splitlines()

    chunks: list[DiffChunk] = []

    for chunk_index, start_index in enumerate(
        range(0, len(patch_lines), max_lines_per_chunk)
    ):
        selected_lines = patch_lines[
            start_index : start_index + max_lines_per_chunk
        ]

        if not selected_lines:
            continue

        chunks.append(
            DiffChunk(
                file_path=filename,
                chunk_index=chunk_index,
                start_line=start_index + 1,
                end_line=start_index + len(selected_lines),
                content="\n".join(selected_lines),
            )
        )

    return chunks


def build_review_input(
    pull_request: dict[str, Any],
    changed_files: list[dict[str, Any]],
) -> ReviewInput:
    """
    Convert GitHub API responses into ReviewInput.
    """

    repository = pull_request.get(
        "base",
        {},
    ).get(
        "repo",
        {},
    ).get(
        "full_name"
    )

    if not repository:
        repository = pull_request.get(
            "head",
            {},
        ).get(
            "repo",
            {},
        ).get(
            "full_name"
        )

    if not repository:
        raise ValueError(
            "Could not determine the repository name."
        )

    pr_number = pull_request.get("number")

    if pr_number is None:
        raise ValueError(
            "Pull request number is missing."
        )

    author = pull_request.get(
        "user",
        {},
    ).get(
        "login",
        "unknown",
    )

    commit_sha = pull_request.get(
        "head",
        {},
    ).get(
        "sha",
        "",
    )

    review_files: list[ReviewFileInput] = []

    for changed_file in changed_files:
        filename = changed_file.get("filename")

        if not filename:
            continue

        chunks = create_chunks_from_patch(
            filename=filename,
            patch=changed_file.get("patch"),
        )

        review_files.append(
            ReviewFileInput(
                filename=filename,
                file_type=classify_file(filename),
                status=changed_file.get(
                    "status",
                    "modified",
                ),
                additions=int(
                    changed_file.get(
                        "additions",
                        0,
                    )
                ),
                deletions=int(
                    changed_file.get(
                        "deletions",
                        0,
                    )
                ),
                chunks=chunks,
            )
        )

    return ReviewInput(
        repo_full_name=repository,
        pr_number=int(pr_number),
        title=pull_request.get(
            "title",
            "Untitled Pull Request",
        ),
        author=author,
        commit_sha=commit_sha,
        files=review_files,
    )