import uuid
import json
from typing import Generator
from curl_cffi import requests

from ..base import Provider


ALIASES = {"fast": "instant", "thorough": "high"}
VALID = {"instant", "low", "medium", "high"}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
BASE_URL = "https://chat.inceptionlabs.ai"
SESSION_ENDPOINT = f"{BASE_URL}/api/session"
CHAT_ENDPOINT = f"{BASE_URL}/api/chat"


class MercuryProvider(Provider):

    def __init__(self, proxy: str = None):
        self.proxy = proxy

    def _create_session(self) -> requests.Session:
        session = requests.Session(impersonate="chrome124")
        
        session.headers.update({
            "User-Agent": UA,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
            "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=1, i",
        })

        if self.proxy:
            session.proxies = {"all": self.proxy}

        return session

    def _normalize_effort(self, effort: str) -> str:
        normalized = ALIASES.get(effort or "medium", effort or "medium")
        return normalized if normalized in VALID else "medium"

    def _get_session_token(self, session: requests.Session) -> str:
        resp = session.get(SESSION_ENDPOINT, timeout=30)
        resp.raise_for_status()

        token = resp.json().get("token")
        if not token:
            raise RuntimeError("session token missing in /api/session response")

        return token

    def _build_chat_payload(self, prompt: str, model: str, effort: str) -> dict:
        message_id = str(uuid.uuid4())
        return {
            "id": str(uuid.uuid4()),
            "model": model,
            "reasoning_effort": effort,
            "trigger": "submit-message",
            "messageId": message_id,
            "messages": [
                {
                    "id": message_id,
                    "role": "user",
                    "parts": [{"type": "text", "text": prompt}],
                }
            ],
        }

    def _post_chat(self, session: requests.Session, payload: dict, stream: bool):
        last_error = ""

        for attempt in range(2):
            session_token = self._get_session_token(session)
            resp = session.post(
                CHAT_ENDPOINT,
                headers={
                    "x-session-token": session_token,
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                },
                json=payload,
                timeout=180,
                stream=stream,
            )

            if resp.status_code in (401, 403):
                last_error = f"Mercury auth failed with status {resp.status_code}"
                continue

            if resp.status_code >= 500 and attempt == 0:
                last_error = f"Mercury upstream transient error {resp.status_code}"
                continue

            if resp.status_code >= 400:
                body = (resp.text or "").strip().replace("\n", " ")
                raise RuntimeError(f"Mercury upstream {resp.status_code}: {body[:500]}")

            return resp

        raise RuntimeError(last_error or "Mercury request failed")

    def _iter_sse_events(self, response):
        for line in response.iter_lines():
            if not line:
                continue

            line_str = line.decode("utf-8", errors="replace").strip()
            if not line_str.startswith("data:"):
                continue

            data_str = line_str[5:].strip()
            if data_str == "[DONE]":
                break

            try:
                yield json.loads(data_str)
            except json.JSONDecodeError:
                continue

    def _build_prompt(self, messages: list[dict]) -> str:
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

    def _call_mercury(self, prompt: str, model: str) -> str:
        session = self._create_session()
        try:
            # Prime cookies required by the public chat app.
            session.get(BASE_URL, timeout=30)

            effort = self._normalize_effort("medium")
            payload = self._build_chat_payload(prompt, model, effort)
            resp = self._post_chat(session, payload, stream=True)

            parts: list[str] = []
            for event in self._iter_sse_events(resp):
                event_type = event.get("type")
                if event_type == "text-delta":
                    delta = event.get("delta", "")
                    if delta:
                        parts.append(delta)
                elif event_type == "error":
                    raise RuntimeError(f"Mercury stream error: {event}")

            return "".join(parts)
        finally:
            session.close()

    def _stream_mercury(self, prompt: str, model: str) -> Generator[str, None, None]:
        session = self._create_session()
        try:
            session.get(BASE_URL, timeout=30)

            effort = self._normalize_effort("medium")
            payload = self._build_chat_payload(prompt, model, effort)
            resp = self._post_chat(session, payload, stream=True)

            for event in self._iter_sse_events(resp):
                event_type = event.get("type")
                if event_type == "text-delta":
                    delta = event.get("delta", "")
                    if delta:
                        yield delta
                elif event_type == "error":
                    raise RuntimeError(f"Mercury stream error: {event}")
        finally:
            session.close()

    def send_message(self, messages: list[dict], model: str = "mercury-2") -> str:
        prompt = self._build_prompt(messages)
        return self._call_mercury(prompt, model)

    def stream_message_live(self, messages: list[dict], model: str = "mercury-2") -> Generator[str, None, None]:
        prompt = self._build_prompt(messages)
        yield from self._stream_mercury(prompt, model)
