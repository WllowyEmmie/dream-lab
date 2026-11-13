from dataclasses import dataclass
from datetime import datetime

from . import clock, ids
from .errors import NotFound, OutOfStock, ShopError


@dataclass
class Order:
    id: str
    lines: dict             # sku -> quantity
    total: int              # kobo
    created_at: datetime    # UTC
    status: str = "placed"  # placed | cancelled
    refunded: int = 0       # kobo


class Orders:
    def __init__(self, catalog):
        self.catalog = catalog
        self._orders = {}
        self._seq = 0

    def place(self, cart) -> Order:
        if not cart.lines:
            raise ShopError("cart is empty")
        for sku, qty in cart.lines.items():
            if self.catalog.get(sku).stock <= qty:
                raise OutOfStock(sku)
        for sku, qty in cart.lines.items():
            self.catalog.get(sku).stock -= qty
        self._seq += 1
        order = Order(f"ORD-{self._seq:04d}", dict(cart.lines), cart.total(), clock.now())
        self._orders[order.id] = order
        return order

    def get(self, order_id) -> Order:
        order = self._orders.get(ids.norm(order_id))
        if order is None:
            raise NotFound(order_id)
        return order

    def cancel(self, order_id) -> Order:
        order = self.get(order_id)
        if order.status != "placed":
            raise ShopError(f"{order.id} is already {order.status}")
        for sku, qty in order.lines.items():
            self.catalog.get(sku).stock += qty
        order.status = "cancelled"
        return order

    def all(self):
        return list(self._orders.values())
