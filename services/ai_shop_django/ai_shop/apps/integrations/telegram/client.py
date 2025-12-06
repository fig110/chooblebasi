import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class TelegramClient:
    def __init__(self, bot_token: str):
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required for Telegram interactions.")
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.http = httpx.Client(timeout=10)

    def send_message(self, chat_id: str, text: str, parse_mode: Optional[str] = None, reply_to: Optional[str] = None) -> Optional[str]:
        payload: Dict[str, Any] = {"chat_id": chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        data = self._post("sendMessage", payload)
        return str(data.get("message_id")) if data else None

    def edit_message(self, chat_id: str, message_id: str, text: str, parse_mode: Optional[str] = None) -> None:
        payload: Dict[str, Any] = {"chat_id": chat_id, "message_id": int(message_id), "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        self._post("editMessageText", payload)

    def send_chat_action(self, chat_id: str, action: str = "typing") -> None:
        payload = {"chat_id": chat_id, "action": action}
        self._post("sendChatAction", payload)

    def send_photo(self, chat_id: str, photo: str, caption: Optional[str] = None, parse_mode: Optional[str] = None) -> Optional[str]:
        payload: Dict[str, Any] = {"chat_id": chat_id, "photo": photo}
        if caption:
            payload["caption"] = caption
        if parse_mode:
            payload["parse_mode"] = parse_mode
        data = self._post("sendPhoto", payload)
        return str(data.get("message_id")) if data else None

    def _post(self, path: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{path}"
        try:
            resp = self.http.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                logger.warning("Telegram API returned failure: %s", data)
                return None
            return data.get("result")
        except httpx.HTTPError as exc:  # pragma: no cover - network
            logger.error("Failed calling Telegram API %s: %s", path, exc)
            return None
