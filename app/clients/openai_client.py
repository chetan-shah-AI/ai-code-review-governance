from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.schemas.llm import AIReviewResponse


class OpenAIReviewClient:
    """
    Real OpenAI client used by the manual Week 5 script.
    Unit tests should use fake clients instead.
    """

    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is missing from .env")

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
    )
    def review_code_chunk(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> AIReviewResponse:
        response = self.client.responses.parse(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
            text_format=AIReviewResponse,
        )

        return response.output_parsed