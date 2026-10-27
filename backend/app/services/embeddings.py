from functools import lru_cache

from fastembed import TextEmbedding

from app.core.config import BASE_DIR, settings


@lru_cache
def _get_model() -> TextEmbedding:
    """Loads the model once and reuses it (loading is slow)."""
    return TextEmbedding(
        model_name=settings.embedding_model,
        cache_dir=str(BASE_DIR / settings.model_cache_dir),
    )


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Turns document chunks into vectors."""
    return [vector.tolist() for vector in _get_model().embed(texts)]


def embed_query(text: str) -> list[float]:
    """Turns a user question into a vector."""
    return next(iter(_get_model().query_embed(text))).tolist()