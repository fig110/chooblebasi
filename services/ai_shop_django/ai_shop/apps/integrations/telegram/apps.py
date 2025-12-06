from django.apps import AppConfig


class TelegramIntegrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ai_shop.apps.integrations.telegram"
    verbose_name = "Telegram Integration"
