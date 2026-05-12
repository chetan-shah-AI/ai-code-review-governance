from pydantic import BaseModel


class DiffChunk(BaseModel):
    file_path: str
    chunk_index: int
    start_line: int | None = None
    end_line: int | None = None
    content: str


class ReviewFileInput(BaseModel):
    filename: str
    file_type: str
    status: str
    additions: int
    deletions: int
    chunks: list[DiffChunk]


class ReviewInput(BaseModel):
    repo_full_name: str
    pr_number: int
    title: str | None = None
    author: str | None = None
    commit_sha: str | None = None
    files: list[ReviewFileInput]