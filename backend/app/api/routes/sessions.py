from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_assistant, get_assistant_service
from app.models import Assistant
from app.schemas import ConversationSessionCreate, ConversationSessionRead
from app.services.assistants import AssistantService

router = APIRouter(prefix="/assistants/{assistant_id}/sessions", tags=["sessions"])


@router.get("/", response_model=list[ConversationSessionRead])
async def list_sessions(assistant: Assistant = Depends(get_assistant)) -> list[ConversationSessionRead]:
    return [ConversationSessionRead.model_validate(session) for session in assistant.sessions]


@router.post("/", response_model=ConversationSessionRead, status_code=201)
async def create_session(
    payload: ConversationSessionCreate,
    assistant: Assistant = Depends(get_assistant),
    service: AssistantService = Depends(get_assistant_service),
) -> ConversationSessionRead:
    session = await service.create_session(assistant, payload)
    return ConversationSessionRead.model_validate(session)
