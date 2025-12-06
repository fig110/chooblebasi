import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from django.db import transaction

from .dtos import ConversationRef, MessageIn, MessageOut, Role, UserRef
from .models import Conversation, Msg, ProviderLink
from .tools import (
    add_product_to_cart,
    remove_product_from_cart,
    search_products,
    view_cart,
)
from .ports import OutboundPort, TypingPort


@dataclass
class DetectedIntent:
    intent: str
    query: str = ""
    product_id: Optional[int] = None
    quantity: int = 1
    max_price: Optional[Decimal] = None
    category: Optional[str] = None


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

        reply_text = self._respond(provider_link, incoming)
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

    def _respond(self, provider_link: ProviderLink, incoming: MessageIn) -> str:
        if not incoming.text:
            return "I didn't catch that. Try asking for a product or your cart."

        intent = self._detect_intent(incoming.text)
        if intent.intent == "view_cart":
            return self._render_cart(provider_link)

        if intent.intent == "add_to_cart":
            return self._handle_add(provider_link, intent)

        if intent.intent == "remove_from_cart":
            return self._handle_remove(provider_link, intent)

        return self._handle_search(intent)

    def _detect_intent(self, text: str) -> DetectedIntent:
        lowered = text.lower()
        numbers = [int(n) for n in re.findall(r"\b(\d+)\b", text)]
        product_id = numbers[-1] if numbers else None
        quantity = numbers[0] if len(numbers) > 1 else 1

        max_price = self._detect_price(lowered)
        if any(keyword in lowered for keyword in ["remove", "delete", "drop"]):
            return DetectedIntent(
                intent="remove_from_cart",
                product_id=product_id,
                quantity=1,
            )

        if any(keyword in lowered for keyword in ["add", "buy", "purchase", "cart"]):
            if "cart" in lowered and not any(word in lowered for word in ["add", "remove", "delete"]):
                return DetectedIntent(intent="view_cart")
            return DetectedIntent(
                intent="add_to_cart",
                product_id=product_id,
                quantity=max(quantity, 1),
            )

        if "cart" in lowered or "basket" in lowered:
            return DetectedIntent(intent="view_cart")

        return DetectedIntent(
            intent="search",
            query=text,
            max_price=max_price,
            category=self._detect_category(lowered),
        )

    def _detect_price(self, lowered: str) -> Optional[Decimal]:
        match = re.search(r"under\s*\$?(\d+(?:\.\d{1,2})?)", lowered)
        if not match:
            match = re.search(r"<(\d+(?:\.\d{1,2})?)", lowered)
        if match:
            try:
                return Decimal(match.group(1))
            except Exception:
                return None
        return None

    def _detect_category(self, lowered: str) -> Optional[str]:
        for hint in ["shoes", "electronics", "books", "clothing", "home"]:
            if hint in lowered:
                return hint
        return None

    def _render_cart(self, provider_link: ProviderLink) -> str:
        lines, total = view_cart(provider_link)
        if not lines:
            return "Your cart is empty. Try asking me to find something to add."

        parts = ["Here is your cart:"]
        for line in lines:
            parts.append(
                f"- {line.product.name} (#{line.product.id}) x{line.quantity}: ${line.subtotal}"
            )
        parts.append(f"**Total:** ${total}")
        return "\n".join(parts)

    def _handle_add(self, provider_link: ProviderLink, intent: DetectedIntent) -> str:
        if intent.product_id is None:
            return "Tell me which product ID to add to your cart."
        success, product = add_product_to_cart(
            provider_link, intent.product_id, quantity=intent.quantity
        )
        if not success or not product:
            return "I couldn't find that product to add."
        quantity_text = f"x{intent.quantity} " if intent.quantity > 1 else ""
        return f"Added {quantity_text}{product.name} (#{product.id}) to your cart."

    def _handle_remove(self, provider_link: ProviderLink, intent: DetectedIntent) -> str:
        if intent.product_id is None:
            return "Tell me which product ID to remove from your cart."
        removed, product = remove_product_from_cart(provider_link, intent.product_id)
        if not removed:
            return "That item was not in your cart."
        return f"Removed {product.name} (#{product.id}) from your cart."

    def _handle_search(self, intent: DetectedIntent) -> str:
        results = search_products(
            query=intent.query,
            max_price=intent.max_price,
            category=intent.category,
        )
        if not results:
            return "I couldn't find matching products. Try a different search."
        lines = ["Here are some options:"]
        for product in results:
            lines.append(
                f"- {product.name} (#{product.id}): ${product.price} — {product.description[:80]}"
            )
        lines.append("Reply with 'add <product_id>' to add an item to your cart.")
        return "\n".join(lines)

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
