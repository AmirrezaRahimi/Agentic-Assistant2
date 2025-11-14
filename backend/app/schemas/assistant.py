import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AssistantBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    system_prompt: Optional[str] = None


class AssistantCreate(AssistantBase):
    pass


class AssistantUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    system_prompt: Optional[str] = None


class AssistantRead(AssistantBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeDocumentBase(BaseModel):
    title: str
    content: str


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    pass


class KnowledgeDocumentRead(KnowledgeDocumentBase):
    id: uuid.UUID
    created_at: datetime
    assistant_id: uuid.UUID

    class Config:
        from_attributes = True


class ConversationSessionBase(BaseModel):
    title: Optional[str] = None


class ConversationSessionCreate(ConversationSessionBase):
    pass


class ConversationSessionRead(ConversationSessionBase):
    id: uuid.UUID
    assistant_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    role: str
    content: str


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: uuid.UUID
    session_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ChatTurn(BaseModel):
    user_message: str


class ChatResponse(BaseModel):
    assistant_message: str
    session: ConversationSessionRead
    messages: list[MessageRead]
