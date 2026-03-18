import uuid
from typing import Generator
from curl_cffi import requests

from ..base import Provider


ALIASES = {"fast": "instant", "thorough": "high"}
VALID = {"instant", "low", "medium", "high"}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
BASE_URL = "https://chat.inceptionlabs.ai"
ENDPOINT = f"{BASE_URL}/api/chat/completions"


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
        
        session_id = str(uuid.uuid4())

        session.get(BASE_URL, timeout=15)

        payload = {
            "model": model, 
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "reasoning_effort": "medium",
        }

        resp = session.post(
            ENDPOINT,
            headers={"x-guest-session-id": session_id, "Content-Type": "application/json", "Accept": "application/json"},
            json=payload,
            timeout=180,
        )

        if resp.status_code == 403:
            session.close()
            session = self._create_session()
            session.get(BASE_URL, timeout=15)
            resp = session.post(
                ENDPOINT,
                headers={"x-guest-session-id": session_id, "Content-Type": "application/json", "Accept": "application/json"},
                json=payload,
                timeout=180,
            )

        resp.raise_for_status()
        raw = resp.json()

        choices = raw.get("choices", [])
        msg = choices[0].get("message", {}) if choices else {}
        text = msg.get("content") or raw.get("content", "")
        
        session.close()
        
        return text

    def _stream_mercury(self, prompt: str, model: str) -> Generator[str, None, None]:
        session = self._create_session()
        session_id = str(uuid.uuid4())
        session.get(BASE_URL, timeout=15)

        payload = {
            "model": model, 
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            "reasoning_effort": "medium",
        }

        resp = session.post(
            ENDPOINT,
            headers={"x-guest-session-id": session_id, "Content-Type": "application/json", "Accept": "application/json"},
            json=payload,
            timeout=180,
            stream=True,
        )

        if resp.status_code == 403:
            session.close()
            session = self._create_session()
            session.get(BASE_URL, timeout=15)
            resp = session.post(
                ENDPOINT,
                headers={"x-guest-session-id": session_id, "Content-Type": "application/json", "Accept": "application/json"},
                json=payload,
                timeout=180,
                stream=True,
            )

        resp.raise_for_status()

        import json
        for line in resp.iter_lines():
            if not line:
                continue
            line_str = line.decode('utf-8')
            if not line_str.startswith("data: "):
                continue
            
            data_str = line_str[6:]
            if data_str == "[DONE]":
                break
            
            try:
                data = json.loads(data_str)
                choices = data.get("choices", [])
                if not choices:
                    continue
                delta = choices[0].get("delta", {})
                content = delta.get("content")
                if content:
                    yield content
            except json.JSONDecodeError:
                pass
                
        session.close()

    def send_message(self, messages: list[dict], model: str = "mercury-2") -> str:
        prompt = self._build_prompt(messages)
        return self._call_mercury(prompt, model)

    def stream_message_live(self, messages: list[dict], model: str = "mercury-2") -> Generator[str, None, None]:
        prompt = self._build_prompt(messages)
        yield from self._stream_mercury(prompt, model)
