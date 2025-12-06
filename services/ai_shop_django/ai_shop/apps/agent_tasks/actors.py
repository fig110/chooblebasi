import logging

import dramatiq
from django.conf import settings

from ai_shop.apps.agent_core.dtos import MessageIn
from ai_shop.apps.agent_core.runtime import AgentRuntime
from ai_shop.apps.integrations.telegram.adapters import TelegramOutbound

logger = logging.getLogger(__name__)


@dramatiq.actor
def run_agent_turn(msg: dict) -> None:
    message = MessageIn.from_dict(msg)
    outbound = TelegramOutbound(bot_token=settings.TELEGRAM_BOT_TOKEN)
    runtime = AgentRuntime(outbound=outbound, typing=outbound)
    runtime.handle_turn(message)
