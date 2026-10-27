import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.llm import LLMError, generate_answer  # noqa: E402

try:
    answer = generate_answer(
        "You are a helpful assistant. Answer in one short sentence.",
        "What does HR stand for?",
    )
    print("LLM replied:", answer)
except LLMError as exc:
    print("LLM error:", exc, "| cause:", repr(exc.__cause__))