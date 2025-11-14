from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import assistants, chat, knowledge, sessions
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

logger = logging.getLogger(__name__)
settings = get_settings()


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def create_application() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(assistants.router, prefix=settings.api_v1_str)
    app.include_router(knowledge.router, prefix=settings.api_v1_str)
    app.include_router(sessions.router, prefix=settings.api_v1_str)
    app.include_router(chat.router, prefix=settings.api_v1_str)

    @app.on_event("startup")
    async def startup_event() -> None:  # pragma: no cover - executed by FastAPI
        await init_models()

    return app


app = create_application()
