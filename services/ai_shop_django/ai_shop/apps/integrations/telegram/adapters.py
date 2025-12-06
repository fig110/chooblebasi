from typing import Optional

from ai_shop.apps.agent_core.dtos import ConversationRef, MessageOut
from ai_shop.apps.agent_core.ports import OutboundPort, TypingPort

from .client import TelegramClient


class TelegramOutbound(OutboundPort, TypingPort):
    def __init__(self, bot_token: str):
        self.client = TelegramClient(bot_token)

    def _chat_id(self, conv: ConversationRef) -> str:
        if conv.key.startswith("telegram:"):
            return conv.key.split(":", 1)[1]
        return conv.key

    def _parse_mode(self, format_hint: Optional[str]) -> Optional[str]:
        if not format_hint:
            return None
        if format_hint.lower() in {"md", "markdown"}:
            return "Markdown"
        if format_hint.lower() == "html":
            return "HTML"
        return None

    def send(self, msg: MessageOut) -> Optional[str]:
        chat_id = self._chat_id(msg.conv)
        parse_mode = self._parse_mode(msg.format_hint)
        return self.client.send_message(chat_id, msg.text, parse_mode=parse_mode, reply_to=msg.reply_to)

    def edit(self, conv: ConversationRef, message_id: str, text: str, format_hint: str = "plain") -> None:
        chat_id = self._chat_id(conv)
        parse_mode = self._parse_mode(format_hint)
        self.client.edit_message(chat_id, message_id, text, parse_mode=parse_mode)

    def typing(self, conv: ConversationRef, on: bool = True) -> None:
        if not on:
            return
        chat_id = self._chat_id(conv)
        self.client.send_chat_action(chat_id)
