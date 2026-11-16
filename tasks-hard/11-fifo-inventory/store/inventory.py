"""Stock valued first-in, first-out."""
from .errors import OutOfStock


class Inventory:
    def __init__(self):
        self._layers = []

    def receive(self, qty: int, unit_cost: int) -> None:
        raise NotImplementedError

    def ship(self, qty: int) -> int:
        raise NotImplementedError

    def units(self) -> int:
        raise NotImplementedError

    def value(self) -> int:
        raise NotImplementedError

    def layers(self) -> list:
        raise NotImplementedError

    def average_cost(self) -> int:
        raise NotImplementedError
