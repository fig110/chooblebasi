from decimal import Decimal

from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=128, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - repr helper
        return f"{self.name} (${self.price})"
