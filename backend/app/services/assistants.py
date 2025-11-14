from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Assistant, ConversationSession, KnowledgeDocument
from app.schemas import AssistantCreate, AssistantUpdate, ConversationSessionCreate, KnowledgeDocumentCreate
from app.services.rag import RAGPipeline


class AssistantService:
    def __init__(self, db: AsyncSession, rag_pipeline: RAGPipeline) -> None:
        self.db = db
        self.rag = rag_pipeline

    async def list_assistants(self) -> list[Assistant]:
        stmt = select(Assistant).order_by(Assistant.created_at.desc())
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_assistant(self, assistant_id: uuid.UUID) -> Assistant:
        stmt = select(Assistant).where(Assistant.id == assistant_id)
        return (await self.db.execute(stmt)).scalar_one()

    async def create_assistant(self, payload: AssistantCreate) -> Assistant:
        assistant = Assistant(**payload.model_dump())
        self.db.add(assistant)
        await self.db.commit()
        await self.db.refresh(assistant)
        return assistant

    async def update_assistant(self, assistant: Assistant, payload: AssistantUpdate) -> Assistant:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(assistant, field, value)
        await self.db.commit()
        await self.db.refresh(assistant)
        return assistant

    async def delete_assistant(self, assistant: Assistant) -> None:
        await self.db.delete(assistant)
        await self.db.commit()

    async def add_document(self, assistant: Assistant, payload: KnowledgeDocumentCreate) -> KnowledgeDocument:
        document = KnowledgeDocument(assistant_id=assistant.id, **payload.model_dump())
        self.db.add(document)
        await self.db.flush()
        await self.rag.ingest_document(self.db, assistant.id, document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def list_documents(self, assistant: Assistant) -> list[KnowledgeDocument]:
        await self.db.refresh(assistant)
        return assistant.knowledge_documents

    async def create_session(
        self, assistant: Assistant, payload: ConversationSessionCreate
    ) -> ConversationSession:
        session = ConversationSession(
            assistant_id=assistant.id,
            title=payload.title or "New Session",
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session
