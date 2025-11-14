from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Assistant, ConversationSession, Message
from app.schemas import ChatResponse, ChatTurn, ConversationSessionRead, MessageRead
from app.services.openai_client import OpenAIClient
from app.services.prompt_builder import PromptBuilder
from app.services.rag import RAGPipeline


class ConversationService:
    def __init__(
        self,
        db: AsyncSession,
        assistant: Assistant,
        rag_pipeline: RAGPipeline,
        openai_client: OpenAIClient,
    ) -> None:
        self.db = db
        self.assistant = assistant
        self.rag = rag_pipeline
        self.openai = openai_client

    async def load_session(self, session_id: uuid.UUID) -> ConversationSession:
        stmt = select(ConversationSession).where(ConversationSession.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one()
        if session.assistant_id != self.assistant.id:
            raise ValueError("Session does not belong to this assistant")
        await self.db.refresh(session)
        return session

    async def create_session(self, title: str | None = None) -> ConversationSession:
        session = ConversationSession(assistant_id=self.assistant.id, title=title or "New Session")
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def add_message(self, session: ConversationSession, role: str, content: str) -> Message:
        message = Message(session_id=session.id, role=role, content=content)
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def chat(self, session: ConversationSession, payload: ChatTurn) -> ChatResponse:
        user_message = payload.user_message
        await self.db.refresh(session)
        history = session.messages
        context = await self.rag.retrieve_context(self.assistant.id, user_message)
        prompt = PromptBuilder(self.assistant, history, context).build(user_message)
        assistant_response = await self.openai.complete(prompt)

        user_msg = await self.add_message(session, "user", user_message)
        assistant_msg = await self.add_message(session, "assistant", assistant_response)
        await self.db.refresh(session)

        return ChatResponse(
            assistant_message=assistant_response,
            session=ConversationSessionRead.model_validate(session),
            messages=[
                MessageRead.model_validate(user_msg),
                MessageRead.model_validate(assistant_msg),
            ],
        )
