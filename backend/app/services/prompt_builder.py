from __future__ import annotations

from typing import Iterable

from app.models import Assistant, Message


class PromptBuilder:
    def __init__(self, assistant: Assistant, history: Iterable[Message], context_chunks: list[str]) -> None:
        self.assistant = assistant
        self.history = list(history)
        self.context_chunks = context_chunks

    def build(self, user_message: str) -> str:
        segments: list[str] = []
        if self.assistant.system_prompt:
            segments.append(f"System Instructions:\n{self.assistant.system_prompt}\n")
        if self.context_chunks:
            segments.append("Relevant Knowledge Snippets:")
            for idx, chunk in enumerate(self.context_chunks, start=1):
                segments.append(f"[{idx}] {chunk}")
        if self.history:
            segments.append("Conversation History:")
            for message in self.history[-10:]:
                segments.append(f"{message.role.title()}: {message.content}")
        segments.append(f"User: {user_message}")
        segments.append("Assistant:")
        return "\n\n".join(segments)
