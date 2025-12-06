from typing import Optional, Protocol

from .dtos import ConversationRef, MessageOut


class InboundPort(Protocol):
    def accept(self, msg: dict) -> None:
        ...


class OutboundPort(Protocol):
    def send(self, msg: MessageOut) -> Optional[str]:
        ...

    def edit(self, conv: ConversationRef, message_id: str, text: str, format_hint: str = "plain") -> None:
        ...


class TypingPort(Protocol):
    def typing(self, conv: ConversationRef, on: bool = True) -> None:
        ...


class MediaPort(Protocol):
    def send_image(self, conv: ConversationRef, path_or_url: str, caption: Optional[str] = None) -> None:
        ...
