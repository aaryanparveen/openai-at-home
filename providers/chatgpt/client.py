
from __future__ import annotations

import logging
from typing import Generator, Optional

from .wrapper import ChatGPT as _RawChatGPT
from ..base import Provider

logger = logging.getLogger("chatgpt-anon")


class AnonChatGPT(Provider):

    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy

    def send_message(self, messages: list[dict], model: str = "auto") -> str:
        prompt = self._build_prompt(messages)
        client = _RawChatGPT(proxy=self.proxy)
        reply = client.ask_question(prompt, model=model)
        return reply or ""

    def stream_message(
        self, messages: list[dict], model: str = "auto"
    ) -> Generator[str, None, None]:
        reply = self.send_message(messages, model)
        if reply:
            yield reply

    def stream_message_live(
        self, messages: list[dict], model: str = "auto"
    ) -> Generator[str, None, None]:
        prompt = self._build_prompt(messages)
        client = _RawChatGPT(proxy=self.proxy)
        yield from client.ask_question_stream(prompt, model=model)

    @staticmethod
    def _build_prompt(messages: list[dict]) -> str:
        formatted_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                formatted_parts.append(f"System Context:\n{content}")
            elif role == "user":
                formatted_parts.append(f"User: {content}")
            elif role == "assistant":
                formatted_parts.append(f"Assistant: {content}")
            else:
                formatted_parts.append(f"{role}: {content}")
        
        return "\n\n".join(formatted_parts)
