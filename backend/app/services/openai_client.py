from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Minimal OpenAI API client with model fallback support."""

    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.openai_api_key:
            logger.warning("OPENAI_API_KEY not configured; responses will be stubbed.")
        self._http_client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={
                "Authorization": f"Bearer {self.settings.openai_api_key}" if self.settings.openai_api_key else "",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(30.0, connect=10.0),
        )

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        if not self.settings.openai_api_key:
            return "OpenAI API key missing. This is a stubbed response based on the prompt."

        payload = {
            "model": self.settings.openai_model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        }
        payload.update(kwargs)

        try:
            response = await self._http_client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except httpx.HTTPError as exc:
            logger.error("Primary model request failed: %s", exc)
            if self.settings.openai_fallback_model == self.settings.openai_model:
                raise
            payload["model"] = self.settings.openai_fallback_model
            response = await self._http_client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not self.settings.openai_api_key:
            logger.info("Using deterministic stub embeddings for %d texts", len(texts))
            return [self._fallback_embedding(t) for t in texts]

        payload = {
            "model": self.settings.embedding_model,
            "input": texts,
        }

        response = await self._http_client.post("/embeddings", json=payload)
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]

    async def aclose(self) -> None:
        await self._http_client.aclose()

    @staticmethod
    def _fallback_embedding(text: str) -> list[float]:
        # Simple hashing-based embedding for offline mode
        seed = sum(ord(ch) for ch in text)
        return [(seed % (i + 13)) / 13.0 for i in range(1536)]


async def get_openai_client() -> OpenAIClient:
    return OpenAIClient()
