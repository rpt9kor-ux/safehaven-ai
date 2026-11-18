import time
from functools import lru_cache

from google import genai
from google.genai import errors, types

from app.core.config import settings

MAX_ATTEMPTS = 3


class LLMError(Exception):
    """Raised when the AI service cannot produce an answer."""


@lru_cache
def _get_client() -> genai.Client:
    if not settings.gemini_api_key:
        raise LLMError("GEMINI_API_KEY is not set in .env")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_answer(system_prompt: str, user_prompt: str) -> str:
    """Sends one prompt to the LLM and returns the text answer.

    Retries a few times on temporary network or server problems.
    """
    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = _get_client().models.generate_content(
                model=settings.llm_model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.2,
                ),
            )
            return (response.text or "").strip()
        except LLMError:
            raise
        except Exception as exc:
            last_error = exc
            # Wrong key, wrong model name, etc. will not fix themselves, so don't retry.
            # 429 (rate limit) is the exception: waiting can help.
            if isinstance(exc, errors.ClientError) and exc.code != 429:
                break
            if attempt < MAX_ATTEMPTS:
                time.sleep(2 * attempt)  # wait 2s, then 4s

    raise LLMError("The AI service is currently unavailable") from last_error