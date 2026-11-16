"""Line and basket pricing."""
from dataclasses import dataclass


@dataclass
class Line:
    name: str
    category: str
    price: int       # kobo, each
    qty: int = 1


def line_total(line) -> int:
    """What a line costs before VAT, in kobo."""
    return line.price * line.qty


def vat(lines) -> int:
    """VAT for a basket, in kobo."""
    return round(sum(line_total(line) for line in lines) * 0.075)


def basket_total(lines) -> int:
    return sum(line_total(line) for line in lines) + vat(lines)
