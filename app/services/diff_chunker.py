import re
from app.schemas.review import DiffChunk


HUNK_HEADER_PATTERN = re.compile(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def chunk_patch(
    file_path: str,
    patch: str | None,
    max_lines: int = 80,
) -> list[DiffChunk]:
    if not patch:
        return []

    lines = patch.splitlines()
    chunks = []

    current_chunk_lines = []
    current_start_line = None
    current_new_line = None
    chunk_index = 0

    for line in lines:
        hunk_match = HUNK_HEADER_PATTERN.match(line)

        if hunk_match:
            current_new_line = int(hunk_match.group(1))

            if current_start_line is None:
                current_start_line = current_new_line

        if current_new_line is not None and current_start_line is None:
            current_start_line = current_new_line

        current_chunk_lines.append(line)

        if current_new_line is not None:
            if line.startswith("+") and not line.startswith("+++"):
                current_new_line += 1
            elif line.startswith("-") and not line.startswith("---"):
                pass
            elif not line.startswith("@@"):
                current_new_line += 1

        if len(current_chunk_lines) >= max_lines:
            chunks.append(
                DiffChunk(
                    file_path=file_path,
                    chunk_index=chunk_index,
                    start_line=current_start_line,
                    end_line=current_new_line,
                    content="\n".join(current_chunk_lines),
                )
            )

            chunk_index += 1
            current_chunk_lines = []
            current_start_line = current_new_line

    if current_chunk_lines:
        chunks.append(
            DiffChunk(
                file_path=file_path,
                chunk_index=chunk_index,
                start_line=current_start_line,
                end_line=current_new_line,
                content="\n".join(current_chunk_lines),
            )
        )

    return chunks


if __name__ == "__main__":
    patch = """@@ -1,3 +1,4 @@
    def hello():
    +    print("hello")
        return True
    """

    chunks = chunk_patch("app/main.py", patch, max_lines=10)

    print("chunks:", chunks)