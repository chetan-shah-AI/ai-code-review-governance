from pathlib import Path

from app.clients.openai_client import OpenAIReviewClient
from app.schemas.findings import Finding, Severity, SourceType
from app.schemas.llm import AIReviewResponse
from app.schemas.review import DiffChunk, ReviewFileInput


PROMPT_PATH = Path("app/prompts/quality_review.txt")


class QualityReviewAgent:
    """
    AI agent responsible for reviewing code quality and maintainability.
    """

    def __init__(self, llm_client: OpenAIReviewClient | None = None):
        self.llm_client = llm_client or OpenAIReviewClient()
        self.system_prompt = PROMPT_PATH.read_text()

    def review_file(self, review_file: ReviewFileInput) -> list[Finding]:
        """
        Review all diff chunks for one changed file.
        """

        findings: list[Finding] = []

        for chunk in review_file.chunks:
            chunk_findings = self.review_chunk(
                review_file=review_file,
                chunk=chunk,
            )

            findings.extend(chunk_findings)

        return findings

    def review_chunk(
        self,
        review_file: ReviewFileInput,
        chunk: DiffChunk,
    ) -> list[Finding]:
        """
        Review one diff chunk using the LLM.
        """

        user_prompt = self._build_user_prompt(
            review_file=review_file,
            chunk=chunk,
        )

        ai_response = self.llm_client.review_code_chunk(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
        )

        return self._convert_ai_response_to_findings(ai_response)

    def _build_user_prompt(
        self,
        review_file: ReviewFileInput,
        chunk: DiffChunk,
    ) -> str:
        """
        Build the prompt sent to the AI for one diff chunk.
        """

        return (
            f"Repository file: {review_file.filename}\n"
            f"File type: {review_file.file_type}\n"
            f"GitHub status: {review_file.status}\n"
            f"Additions: {review_file.additions}\n"
            f"Deletions: {review_file.deletions}\n"
            f"Chunk index: {chunk.chunk_index}\n"
            f"Approximate new-file lines: {chunk.start_line} to {chunk.end_line}\n\n"
            f"Diff chunk:\n"
            f"```diff\n"
            f"{chunk.content}\n"
            f"```"
        )

    def _convert_ai_response_to_findings(
        self,
        ai_response: AIReviewResponse,
    ) -> list[Finding]:
        """
        Convert AI response into the shared Finding schema.
        """

        findings: list[Finding] = []

        for item in ai_response.findings:
            findings.append(
                Finding(
                    file_path=item.file_path,
                    line_number=item.line_number,
                    severity=Severity(item.severity),
                    category=item.category,
                    title=item.title,
                    description=item.description,
                    recommendation=item.recommendation,
                    source_type=SourceType.AI,
                    tool_name="quality_review_agent",
                    confidence=item.confidence,
                )
            )

        return findings