import json
import logging
from typing import Any, Dict, Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ai_shop.apps.agent_core.dtos import ConversationRef, MessageIn, Role, UserRef
from ai_shop.apps.agent_tasks.actors import run_agent_turn

logger = logging.getLogger(__name__)


def _extract_message(update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if "message" in update and isinstance(update["message"], dict):
        msg = update["message"]
        if "text" in msg and "chat" in msg:
            return msg
    return None


@csrf_exempt
def telegram_webhook(request: HttpRequest, secret: str) -> HttpResponse:
    if secret != settings.TG_WEBHOOK_SECRET:
        return HttpResponseForbidden("invalid webhook secret")
    if request.method != "POST":
        return HttpResponseBadRequest("only POST supported")

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("invalid JSON")

    incoming_message = _extract_message(payload)
    if not incoming_message:
        logger.info("Ignoring update without text message: %s", payload)
        return JsonResponse({"ok": True, "skipped": True})

    chat = incoming_message.get("chat", {})
    chat_id = str(chat.get("id"))
    text = incoming_message.get("text", "")

    msg_in = MessageIn(
        conv=ConversationRef(key=f"telegram:{chat_id}"),
        user=UserRef(provider="telegram", provider_user_id=chat_id),
        role=Role.USER,
        text=text,
        meta={"raw": incoming_message},
    )

    run_agent_turn.send(msg_in.to_dict())
    return JsonResponse({"ok": True})
