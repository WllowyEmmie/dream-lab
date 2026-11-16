"""Invoices for orders."""
from dataclasses import dataclass


@dataclass
class Line:
    name: str
    category: str
    price: int       # kobo, each
    qty: int = 1


def make_invoice(order_ref: str, lines) -> dict:
    """Build the invoice for an order."""
    raise NotImplementedError
