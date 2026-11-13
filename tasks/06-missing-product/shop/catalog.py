from dataclasses import dataclass

from . import ids, money
from .errors import NotFound


@dataclass
class Product:
    sku: str
    name: str
    price: int          # kobo
    stock: int = 0
    weight_g: int = 0


class Catalog:
    def __init__(self):
        self._items = {}

    def add(self, sku, name, price_naira, stock=0, weight_g=0) -> Product:
        """Add a product. price_naira is a string like "19.99"."""
        product = Product(ids.norm(sku), name, money.to_kobo(price_naira), stock, weight_g)
        self._items[product.sku] = product
        return product

    def get(self, sku) -> Product:
        return self._items.get(ids.norm(sku))

    def all(self):
        return list(self._items.values())
