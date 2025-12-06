from decimal import Decimal
from typing import List, Optional, Tuple

from django.db.models import Q

from ai_shop.apps.orders.services import CartService
from ai_shop.apps.products.models import Product

from .models import ProviderLink


def search_products(
    query: str,
    max_price: Optional[Decimal] = None,
    category: Optional[str] = None,
    limit: int = 5,
) -> List[Product]:
    qs = Product.objects.filter(is_active=True)
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category:
        qs = qs.filter(category__icontains=category)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    return list(qs.order_by("name")[:limit])


def view_cart(provider_link: ProviderLink):
    service = CartService(provider_link)
    return service.as_lines(), service.total()


def add_product_to_cart(
    provider_link: ProviderLink, product_id: int, quantity: int = 1
) -> Tuple[bool, Optional[Product]]:
    product = Product.objects.filter(id=product_id, is_active=True).first()
    if not product:
        return False, None
    service = CartService(provider_link)
    service.add_product(product, quantity=quantity)
    return True, product


def remove_product_from_cart(
    provider_link: ProviderLink, product_id: int
) -> Tuple[bool, Optional[Product]]:
    product = Product.objects.filter(id=product_id).first()
    if not product:
        return False, None
    service = CartService(provider_link)
    removed = service.remove_product(product)
    return removed, product if removed else product
