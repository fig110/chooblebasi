from django.conf import settings
from django.db import models


class ProviderLink(models.Model):
    provider = models.CharField(max_length=64)
    provider_user_id = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="provider_links", on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("provider", "provider_user_id")
        indexes = [
            models.Index(fields=["provider", "provider_user_id"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - repr helper
        return f"{self.provider}:{self.provider_user_id}"


class Conversation(models.Model):
    key = models.CharField(max_length=255, unique=True)
    provider_link = models.ForeignKey(
        ProviderLink, related_name="conversations", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - repr helper
        return self.key


class Msg(models.Model):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_SYSTEM = "system"

    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_ASSISTANT, "Assistant"),
        (ROLE_SYSTEM, "System"),
    ]

    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    text = models.TextField()
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:  # pragma: no cover - repr helper
        return f"[{self.role}] {self.text[:30]}"
