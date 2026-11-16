"""Stock reservations: units held for a customer while they check out."""
from .errors import NotFound, OutOfStock


class Reservations:
    def __init__(self, stock: dict, now):
        """stock: sku -> units on hand. now: a function returning the time in seconds."""
        self._stock = dict(stock)
        self._now = now

    def on_hand(self, sku) -> int:
        raise NotImplementedError

    def available(self, sku) -> int:
        raise NotImplementedError

    def reserve(self, sku, qty, ttl) -> str:
        raise NotImplementedError

    def confirm(self, reservation_id) -> None:
        raise NotImplementedError

    def release(self, reservation_id) -> None:
        raise NotImplementedError
