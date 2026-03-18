from abc import ABC, abstractmethod
from typing import Any, Generator, Optional


class Provider(ABC):

    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy

    @abstractmethod
    def send_message(self, messages: list[dict], model: str) -> str:
        pass

    @abstractmethod
    def stream_message_live(
        self, messages: list[dict], model: str
    ) -> Generator[str, None, None]:
        pass
