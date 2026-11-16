"""Order totals."""
from dataclasses import dataclass

from . import tax

SHIPPING_FEE = 250_000           # kobo
FREE_SHIPPING_FROM = 5_000_000   # kobo


@dataclass
class Line:
    name: str
    category: str
    price: int       # kobo, each
    qty: int = 1


def totals(lines, discount_percent=0) -> dict:
    """Subtotal, discount, shipping, VAT and total for an order, in kobo."""
    subtotal = sum(line.price * line.qty for line in lines)
    shipping = 0 if subtotal >= FREE_SHIPPING_FROM else SHIPPING_FEE
    discount = subtotal * discount_percent // 100
    vat = tax.vat(subtotal + shipping)
    return {"subtotal": subtotal, "discount": discount, "shipping": shipping, "vat": vat,
            "total": subtotal - discount + shipping + vat}
