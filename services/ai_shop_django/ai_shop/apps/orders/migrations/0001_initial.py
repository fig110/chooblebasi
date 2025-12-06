# Generated manually for initial orders schema
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("agent_core", "0001_initial"),
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cart",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "provider_link",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cart",
                        to="agent_core.providerlink",
                    ),
                ),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                (
                    "cart",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="orders.cart",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cart_items",
                        to="products.product",
                    ),
                ),
            ],
            options={"ordering": ["-added_at"]},
        ),
        migrations.AlterUniqueTogether(
            name="cartitem",
            unique_together={("cart", "product")},
        ),
    ]
