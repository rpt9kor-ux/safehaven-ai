import uuid
from functools import lru_cache

from qdrant_client import QdrantClient, models

from app.core.config import BASE_DIR, settings
from app.services.embeddings import embed_documents, embed_query
from app.services.pdf_processor import Chunk


@lru_cache
def get_client() -> QdrantClient:
    if settings.qdrant_url:
        client = QdrantClient(url=settings.qdrant_url)
    else:
        client = QdrantClient(path=str(BASE_DIR / settings.qdrant_path))

    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(
                size=settings.embedding_dim, distance=models.Distance.COSINE
            ),
        )
    return client


def index_chunks(
    document_id: int, title: str, access_level: str, chunks: list[Chunk]
) -> None:
    """Stores every chunk as a vector, with the details needed for citations."""
    vectors = embed_documents([chunk.text for chunk in chunks])
    points = [
        models.PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "document_id": document_id,
                "title": title,
                "access_level": access_level,
                "page_number": chunk.page_number,
                "text": chunk.text,
            },
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    get_client().upsert(collection_name=settings.qdrant_collection, points=points)


def delete_document_chunks(document_id: int) -> None:
    get_client().delete(
        collection_name=settings.qdrant_collection,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id", match=models.MatchValue(value=document_id)
                    )
                ]
            )
        ),
    )


def search(question: str, allowed_levels: list[str], limit: int = 5) -> list[dict]:
    """Finds the closest chunks, but only from documents the user may see."""
    result = get_client().query_points(
        collection_name=settings.qdrant_collection,
        query=embed_query(question),
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="access_level", match=models.MatchAny(any=allowed_levels)
                )
            ]
        ),
        limit=limit,
        with_payload=True,
    )
    return [{"score": point.score, **point.payload} for point in result.points]