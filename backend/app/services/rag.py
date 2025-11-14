from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import KnowledgeDocument
from app.services.openai_client import OpenAIClient
from app.services.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self, vector_store: VectorStore, openai_client: OpenAIClient) -> None:
        self.vector_store = vector_store
        self.openai_client = openai_client

    async def ingest_document(
        self, session: AsyncSession, assistant_id: uuid.UUID, document: KnowledgeDocument
    ) -> KnowledgeDocument:
        embeddings = await self.openai_client.embed([document.content])
        vector_id = await self.vector_store.upsert_document(
            assistant_id=assistant_id,
            document_id=document.id,
            vector=embeddings[0],
            payload={"title": document.title, "content": document.content[:1500]},
        )
        document.vector_id = vector_id
        await session.flush()
        return document

    async def retrieve_context(self, assistant_id: uuid.UUID, query: str, limit: int = 5) -> list[str]:
        query_embedding = (await self.openai_client.embed([query]))[0]
        results = await self.vector_store.search(assistant_id, query_embedding, limit=limit)
        return [
            result["payload"].get("content", "")
            for result in results
            if result.get("payload")
        ]

    async def bootstrap_assistant(self, session: AsyncSession, assistant_id: uuid.UUID) -> None:
        stmt = select(KnowledgeDocument).where(KnowledgeDocument.assistant_id == assistant_id)
        docs = (await session.execute(stmt)).scalars().all()
        for doc in docs:
            if doc.vector_id:
                continue
            try:
                await self.ingest_document(session, assistant_id, doc)
            except Exception:  # pragma: no cover - log and continue
                logger.exception("Failed to ingest document %s", doc.id)
