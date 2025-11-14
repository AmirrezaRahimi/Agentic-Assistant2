# Vardast Architecture

## Overview

Vardast consists of three primary layers working together to deliver an AI assistant builder experience:

1. **Frontend (Next.js + Tailwind)** — a TypeScript dashboard for managing assistants, uploading knowledge, and chatting in real time.
2. **Backend (FastAPI + Postgres + Qdrant)** — provides REST APIs for CRUD operations, conversation orchestration, and retrieval-augmented generation.
3. **AI Layer (OpenAI + Fallback)** — handles embedding generation, prompt composition, and model inference with graceful degradation if API keys are absent.

## Component Diagram

```
[Next.js UI]
    | REST (HTTPS)
    v
[FastAPI Application]
    |-- SQLAlchemy -> Postgres (assistants, sessions, messages, docs)
    |-- Qdrant Client -> Qdrant (vectorized knowledge)
    |-- OpenAI Client -> GPT-4o mini / Embeddings
```

## Backend Modules

- `app/core/config.py` — Pydantic settings abstraction, environment variable management.
- `app/db/` — SQLAlchemy engine/session configuration and declarative base.
- `app/models/` — ORM models for assistants, knowledge documents, conversation sessions, and messages.
- `app/schemas/` — Pydantic schemas exchanged via the REST API.
- `app/services/` — domain logic:
  - `openai_client.py` — typed async HTTP client with fallback embeddings/completions.
  - `vector_store.py` — Qdrant integration and collection management.
  - `rag.py` — ingestion and retrieval pipeline for knowledge documents.
  - `prompt_builder.py` — merges system prompt, knowledge snippets, and conversation history.
  - `conversation.py` — orchestrates chat sessions and message persistence.
  - `assistants.py` — CRUD + knowledge/session helpers.
- `app/api/routes/` — FastAPI routers grouped by domain (assistants, knowledge, sessions, chat).
- `app/main.py` — application factory, CORS setup, and startup hooks.

## Data Model

- **Assistant** — persona metadata and system prompt.
- **KnowledgeDocument** — textual content plus Qdrant vector ID.
- **ConversationSession** — groups messages per assistant.
- **Message** — chat transcripts tagged by role (`user` or `assistant`).

Relationships are cascaded with `delete-orphan` semantics to simplify cleanup when an assistant is removed.

## Retrieval-Augmented Generation Flow

1. User submits a prompt via the frontend.
2. Backend loads the assistant, session history, and retrieves top knowledge snippets from Qdrant.
3. `PromptBuilder` stitches system instructions, historical turns, and knowledge into a single prompt.
4. `OpenAIClient` calls the configured chat model (fallback to stub if key missing).
5. Responses are stored as `Message` records and returned to the UI alongside the session metadata.

## Frontend Composition

- `app/page.tsx` — client-side dashboard layout orchestrating all widgets.
- `components/AssistantForm.tsx` — create new assistants.
- `components/AssistantList.tsx` — fetch, display, and delete assistants.
- `components/ChatPanel.tsx` — chat UI, knowledge viewer, and uploader.
- `lib/api.ts` — typed fetch helpers targeting the FastAPI backend.

Next.js is configured in `next.config.mjs` with standalone output to ease containerization.

## Testing Strategy

- `backend/tests/` uses pytest with FastAPI's TestClient and in-memory SQLite.
- Dependencies (`get_db`, OpenAI, Qdrant, RAG) are overridden with lightweight stubs for deterministic assertions.
- Tests validate assistant CRUD and chat flows end-to-end.

## Deployment Topology

Docker Compose provisions four services:

- `backend` — FastAPI application container.
- `frontend` — Next.js server.
- `postgres` — persistent relational store.
- `qdrant` — vector database for document embeddings.

Volumes preserve database and vector data, while health checks ensure Postgres readiness before the backend starts.

For production, build images from the provided Dockerfiles and deploy to your preferred orchestration platform (Kubernetes, ECS, etc.). Inject environment variables securely and front the services with TLS termination.
