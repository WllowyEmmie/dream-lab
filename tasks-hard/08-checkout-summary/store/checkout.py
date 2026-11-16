"""Checkout summary shown before payment."""
from dataclasses import dataclass


@dataclass
class Item:
    name: str
    category: str
    price: int       # kobo, each
    qty: int = 1


def summary(items, discount_percent=0) -> dict:
    """Return subtotal, discount, shipping, vat and total, all in kobo."""
    raise NotImplementedError
