# Vardast — Simple AI Assistant Builder

Vardast is a full-stack application that lets teams create AI assistants, ground them with private knowledge, and chat instantly. It ships with a FastAPI backend, a Next.js dashboard, OpenAI-powered reasoning with a deterministic fallback, and infrastructure-as-code for local development.

## Features

- **Assistant management** — create, update, and delete AI personas with custom instructions.
- **Knowledge grounding** — upload textual documents that are vectorized via OpenAI embeddings and stored in Qdrant for retrieval.
- **Chat orchestration** — unified prompt builder merges system instructions, conversation history, and retrieved knowledge before calling GPT-4o mini.
- **Self-host friendly** — Dockerfiles and docker-compose orchestrate FastAPI, Next.js, Postgres, and Qdrant.
- **Test coverage** — backend unit tests validate critical workflows.

## System Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for a component-level overview, data flow, and deployment considerations.

## Getting Started

### Prerequisites

- Docker and docker-compose
- OpenAI API key (optional but recommended)

### Quickstart

```bash
git clone <repo>
cd Agentic-Assistant2
cp .env.example .env
# edit .env with your OpenAI key if available
docker compose up --build
```

Services will be available at:

- Backend API: http://localhost:8000/docs
- Frontend UI: http://localhost:3000
- Postgres: localhost:5432
- Qdrant: http://localhost:6333

### Local Development

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Environment variables may be configured via `.env` in the backend directory. Refer to `.env.example` for a template.

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE` in a `.env.local` file to point at the backend (defaults to `http://localhost:8000/api/v1`).

### Testing

Backend tests use pytest:

```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-asyncio
pytest
```

### Production Deployment

- Use the provided Dockerfiles to build container images.
- Provision Postgres and Qdrant instances (managed or self-hosted).
- Supply environment variables via secure secrets management.
- Configure HTTPS termination (e.g., via a reverse proxy or cloud load balancer).

## API Overview

- `POST /api/v1/assistants/` — create an assistant.
- `GET /api/v1/assistants/` — list assistants.
- `POST /api/v1/assistants/{assistant_id}/knowledge/` — add a knowledge document (ingested into Qdrant).
- `POST /api/v1/chat/assistants/{assistant_id}` — start a chat session and receive a response.
- `POST /api/v1/chat/assistants/{assistant_id}/sessions/{session_id}` — continue an existing session.

Interactive documentation is available at `/docs` when the backend is running.

## License

MIT
