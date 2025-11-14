from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_assistant, get_assistant_service
from app.models import Assistant
from app.schemas import AssistantCreate, AssistantRead, AssistantUpdate
from app.services.assistants import AssistantService

router = APIRouter(prefix="/assistants", tags=["assistants"])


@router.get("/", response_model=list[AssistantRead])
async def list_assistants(service: AssistantService = Depends(get_assistant_service)) -> list[AssistantRead]:
    assistants = await service.list_assistants()
    return [AssistantRead.model_validate(a) for a in assistants]


@router.post("/", response_model=AssistantRead, status_code=201)
async def create_assistant(
    payload: AssistantCreate,
    service: AssistantService = Depends(get_assistant_service),
) -> AssistantRead:
    assistant = await service.create_assistant(payload)
    return AssistantRead.model_validate(assistant)


@router.get("/{assistant_id}", response_model=AssistantRead)
async def get_assistant_detail(assistant: Assistant = Depends(get_assistant)) -> AssistantRead:
    return AssistantRead.model_validate(assistant)


@router.put("/{assistant_id}", response_model=AssistantRead)
async def update_assistant(
    payload: AssistantUpdate,
    assistant: Assistant = Depends(get_assistant),
    service: AssistantService = Depends(get_assistant_service),
) -> AssistantRead:
    assistant = await service.update_assistant(assistant, payload)
    return AssistantRead.model_validate(assistant)


@router.delete(
    "/{assistant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
async def delete_assistant(
    assistant: Assistant = Depends(get_assistant),
    service: AssistantService = Depends(get_assistant_service),
) -> Response:
    await service.delete_assistant(assistant)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
