from functools import lru_cache

from google import genai
from google.genai import types

from app.core.config import settings


class LLMError(Exception):
    """Raised when the AI service cannot produce an answer."""


@lru_cache
def _get_client() -> genai.Client:
    if not settings.gemini_api_key:
        raise LLMError("GEMINI_API_KEY is not set in .env")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_answer(system_prompt: str, user_prompt: str) -> str:
    """Sends one prompt to the LLM and returns the text answer."""
    try:
        response = _get_client().models.generate_content(
            model=settings.llm_model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,  # low = factual and consistent
            ),
        )
        return (response.text or "").strip()
    except LLMError:
        raise
    except Exception as exc:
        raise LLMError("The AI service is currently unavailable") from exc