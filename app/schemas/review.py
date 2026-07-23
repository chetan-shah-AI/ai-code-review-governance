from pydantic import BaseModel


class DiffChunk(BaseModel):
    """
    One smaller section of a GitHub diff.
    """

    file_path: str
    chunk_index: int
    start_line: int | None = None
    end_line: int | None = None
    content: str


class ReviewFileInput(BaseModel):
    """
    One changed file prepared for review.
    """

    filename: str
    file_type: str
    status: str
    additions: int
    deletions: int
    chunks: list[DiffChunk]


class ReviewInput(BaseModel):
    """
    Full pull request input prepared for review.
    """

    repo_full_name: str
    pr_number: int
    title: str | None = None
    author: str | None = None
    commit_sha: str | None = None
    files: list[ReviewFileInput]