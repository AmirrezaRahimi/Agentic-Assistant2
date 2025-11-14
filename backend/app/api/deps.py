from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import Assistant
from app.services import AssistantService, RAGPipeline, get_openai_client, get_vector_store
from app.services.openai_client import OpenAIClient
from app.services.vector_store import VectorStore


async def get_db() -> AsyncSession:
    async for session in get_session():
        try:
            yield session
        finally:
            await session.close()


async def get_vector_service() -> VectorStore:
    return await get_vector_store()


async def get_openai_service() -> OpenAIClient:
    return await get_openai_client()


async def get_rag_pipeline(
    vector_store: VectorStore = Depends(get_vector_service),
    openai_client: OpenAIClient = Depends(get_openai_service),
) -> RAGPipeline:
    return RAGPipeline(vector_store, openai_client)


async def get_assistant_service(
    db: AsyncSession = Depends(get_db),
    rag_pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> AssistantService:
    return AssistantService(db, rag_pipeline)


async def get_assistant(
    assistant_id: uuid.UUID,
    service: AssistantService = Depends(get_assistant_service),
) -> Assistant:
    try:
        return await service.get_assistant(assistant_id)
    except Exception as exc:  # pragma: no cover - FastAPI handles specifics
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found") from exc
