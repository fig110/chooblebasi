from typing import Optional

from django.db import transaction

from .dtos import ConversationRef, MessageIn, MessageOut, Role, UserRef
from .models import Conversation, Msg, ProviderLink
from .ports import OutboundPort, TypingPort


class AgentRuntime:
    def __init__(self, outbound: OutboundPort, typing: Optional[TypingPort] = None):
        self.outbound = outbound
        self.typing_port = typing

    def handle_turn(self, incoming: MessageIn) -> Optional[str]:
        conversation, _ = self._get_or_create_conversation(incoming.conv, incoming.user)

        with transaction.atomic():
            Msg.objects.create(
                conversation=conversation,
                role=incoming.role.value if isinstance(incoming.role, Role) else str(incoming.role),
                text=incoming.text,
                meta=incoming.meta,
            )

        if self.typing_port:
            self.typing_port.typing(incoming.conv, on=True)

        reply_text = f"You said: {incoming.text}" if incoming.text else "I didn't catch that."
        outgoing = MessageOut(conv=incoming.conv, text=reply_text, format_hint="md")
        message_id = self.outbound.send(outgoing)

        with transaction.atomic():
            Msg.objects.create(
                conversation=conversation,
                role=Msg.ROLE_ASSISTANT,
                text=outgoing.text,
                meta={"provider_message_id": message_id} if message_id else {},
            )

        if self.typing_port:
            self.typing_port.typing(incoming.conv, on=False)

        return message_id

    def _get_or_create_conversation(
        self, conv_ref: ConversationRef, user_ref: UserRef
    ) -> tuple[Conversation, Optional[ProviderLink]]:
        provider_link, _ = ProviderLink.objects.get_or_create(
            provider=user_ref.provider,
            provider_user_id=user_ref.provider_user_id,
            defaults={"user": None},
        )
        conversation, _ = Conversation.objects.get_or_create(
            key=conv_ref.key,
            defaults={"provider_link": provider_link},
        )
        if conversation.provider_link_id is None:
            conversation.provider_link = provider_link
            conversation.save(update_fields=["provider_link"])
        return conversation, provider_link
