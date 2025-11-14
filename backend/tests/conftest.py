import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import main as app_main
from app.db import session as db_session

from app.api.deps import get_db, get_openai_service, get_rag_pipeline, get_vector_service
from app.db.base import Base
from app.main import app


class StubOpenAI:
    async def complete(self, prompt: str, **_: object) -> str:
        return "Stubbed response"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 1536 for _ in texts]


class StubVectorStore:
    async def ensure_collection(self, vector_size: int = 1536) -> None:  # pragma: no cover - no-op
        return None

    async def upsert_document(self, *args, **kwargs) -> str:  # pragma: no cover - no-op
        return str(uuid.uuid4())

    async def search(self, *args, **kwargs) -> list[dict]:
        return []


class StubRAG:
    def __init__(self) -> None:
        self.vector_store = StubVectorStore()
        self.openai_client = StubOpenAI()

    async def ingest_document(self, *args, **kwargs):  # pragma: no cover - no-op
        return None

    async def retrieve_context(self, *args, **kwargs) -> list[str]:
        return []

    async def bootstrap_assistant(self, *args, **kwargs):  # pragma: no cover - no-op
        return None


@pytest.fixture(scope="session")
def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    db_session.engine = engine
    db_session.SessionLocal = TestingSessionLocal
    app_main.engine = engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_openai_service] = lambda: StubOpenAI()
    app.dependency_overrides[get_vector_service] = lambda: StubVectorStore()
    app.dependency_overrides[get_rag_pipeline] = lambda: StubRAG()


@pytest.fixture()
def client() -> AsyncGenerator[TestClient, None]:
    with TestClient(app) as test_client:
        yield test_client
