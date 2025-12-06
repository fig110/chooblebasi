from dataclasses import dataclass
from typing import Iterable, List

from django.db import transaction

from ai_shop.apps.agent_core.models import ProviderLink
from ai_shop.apps.products.models import Product

from .models import Cart, CartItem


@dataclass
class CartLine:
    product: Product
    quantity: int

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class CartService:
    def __init__(self, provider_link: ProviderLink):
        self.provider_link = provider_link

    def get_cart(self) -> Cart:
        cart, _ = Cart.objects.get_or_create(provider_link=self.provider_link)
        return cart

    def list_items(self) -> Iterable[CartLine]:
        cart = self.get_cart()
        items = CartItem.objects.filter(cart=cart).select_related("product")
        return [CartLine(product=item.product, quantity=item.quantity) for item in items]

    def add_product(self, product: Product, quantity: int = 1) -> CartItem:
        cart = self.get_cart()
        with transaction.atomic():
            item, created = CartItem.objects.select_for_update().get_or_create(
                cart=cart, product=product, defaults={"quantity": max(quantity, 1)}
            )
            if not created:
                item.quantity += max(quantity, 1)
                item.save(update_fields=["quantity"])
        return item

    def remove_product(self, product: Product) -> bool:
        cart = self.get_cart()
        deleted, _ = CartItem.objects.filter(cart=cart, product=product).delete()
        return deleted > 0

    def clear(self) -> None:
        cart = self.get_cart()
        CartItem.objects.filter(cart=cart).delete()

    def total(self):
        return sum(line.subtotal for line in self.list_items())

    def as_lines(self) -> List[CartLine]:
        return list(self.list_items())
