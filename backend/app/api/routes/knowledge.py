from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_assistant, get_assistant_service
from app.models import Assistant
from app.schemas import KnowledgeDocumentCreate, KnowledgeDocumentRead
from app.services.assistants import AssistantService

router = APIRouter(prefix="/assistants/{assistant_id}/knowledge", tags=["knowledge"])


@router.get("/", response_model=list[KnowledgeDocumentRead])
async def list_documents(
    assistant: Assistant = Depends(get_assistant),
    service: AssistantService = Depends(get_assistant_service),
) -> list[KnowledgeDocumentRead]:
    documents = await service.list_documents(assistant)
    return [KnowledgeDocumentRead.model_validate(doc) for doc in documents]


@router.post("/", response_model=KnowledgeDocumentRead, status_code=201)
async def create_document(
    payload: KnowledgeDocumentCreate,
    assistant: Assistant = Depends(get_assistant),
    service: AssistantService = Depends(get_assistant_service),
) -> KnowledgeDocumentRead:
    document = await service.add_document(assistant, payload)
    return KnowledgeDocumentRead.model_validate(document)
