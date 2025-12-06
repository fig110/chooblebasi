from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class UserRef:
    provider: str
    provider_user_id: str
    internal_user_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "provider_user_id": self.provider_user_id,
            "internal_user_id": self.internal_user_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserRef":
        return cls(
            provider=data["provider"],
            provider_user_id=data["provider_user_id"],
            internal_user_id=data.get("internal_user_id"),
        )


@dataclass
class ConversationRef:
    key: str

    def to_dict(self) -> Dict[str, Any]:
        return {"key": self.key}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationRef":
        return cls(key=data["key"])


@dataclass
class MessageIn:
    conv: ConversationRef
    user: UserRef
    role: Role
    text: str
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conv": self.conv.to_dict(),
            "user": self.user.to_dict(),
            "role": self.role.value,
            "text": self.text,
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageIn":
        return cls(
            conv=ConversationRef.from_dict(data["conv"]),
            user=UserRef.from_dict(data["user"]),
            role=Role(data.get("role", Role.USER)),
            text=data.get("text", ""),
            meta=data.get("meta", {}) or {},
        )


@dataclass
class MessageOut:
    conv: ConversationRef
    text: str
    format_hint: str = "plain"
    reply_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conv": self.conv.to_dict(),
            "text": self.text,
            "format_hint": self.format_hint,
            "reply_to": self.reply_to,
        }
