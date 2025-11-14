from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_assistant, get_db, get_openai_service, get_rag_pipeline
from app.models import Assistant
from app.schemas import ChatResponse, ChatTurn
from app.services.conversation import ConversationService
from app.services.openai_client import OpenAIClient
from app.services.rag import RAGPipeline

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/assistants/{assistant_id}/sessions/{session_id}", response_model=ChatResponse)
async def chat_existing_session(
    payload: ChatTurn,
    assistant: Assistant = Depends(get_assistant),
    session_id: uuid.UUID = Path(..., description="Conversation session identifier"),
    db: AsyncSession = Depends(get_db),
    rag: RAGPipeline = Depends(get_rag_pipeline),
    openai: OpenAIClient = Depends(get_openai_service),
) -> ChatResponse:
    service = ConversationService(db, assistant, rag, openai)
    try:
        session = await service.load_session(session_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found") from exc
    response = await service.chat(session, payload)
    await db.commit()
    return response


@router.post("/assistants/{assistant_id}", response_model=ChatResponse)
async def chat_new_session(
    payload: ChatTurn,
    assistant: Assistant = Depends(get_assistant),
    db: AsyncSession = Depends(get_db),
    rag: RAGPipeline = Depends(get_rag_pipeline),
    openai: OpenAIClient = Depends(get_openai_service),
) -> ChatResponse:
    service = ConversationService(db, assistant, rag, openai)
    session = await service.create_session()
    response = await service.chat(session, payload)
    await db.commit()
    return response
