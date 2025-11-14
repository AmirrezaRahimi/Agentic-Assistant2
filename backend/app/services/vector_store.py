from __future__ import annotations

import logging
import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qdrant_models

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class VectorStore:
    COLLECTION_NAME = "assistant_documents"

    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

    async def ensure_collection(self, vector_size: int = 1536) -> None:
        exists = await self.client.collection_exists(self.COLLECTION_NAME)
        if not exists:
            logger.info("Creating Qdrant collection %s", self.COLLECTION_NAME)
            await self.client.create_collection(
                self.COLLECTION_NAME,
                vectors_config=qdrant_models.VectorParams(size=vector_size, distance=qdrant_models.Distance.COSINE),
            )

    async def upsert_document(self, assistant_id: uuid.UUID, document_id: uuid.UUID, vector: list[float], payload: dict) -> str:
        await self.ensure_collection(len(vector))
        point_id = str(document_id)
        await self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"assistant_id": str(assistant_id), **payload},
                )
            ],
        )
        return point_id

    async def search(self, assistant_id: uuid.UUID, vector: list[float], limit: int = 5) -> list[dict]:
        await self.ensure_collection(len(vector))
        search_result = await self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=vector,
            limit=limit,
            filter=qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="assistant_id", match=qdrant_models.MatchValue(value=str(assistant_id))
                    )
                ]
            ),
        )
        return [
            {
                "id": point.id,
                "score": point.score,
                "payload": point.payload,
            }
            for point in search_result
        ]


async def get_vector_store() -> VectorStore:
    return VectorStore()
