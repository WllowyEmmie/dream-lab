"""Price quotes for business customers."""
from dataclasses import dataclass, field


@dataclass
class QuoteLine:
    description: str
    unit_price: int     # kobo
    qty: int = 1


@dataclass
class Quote:
    customer: str
    handling_percent: float = 0     # handling charge, as a percent of the subtotal
    lines: list = field(default_factory=list)

    def add(self, description, unit_price, qty=1):
        self.lines.append(QuoteLine(description, unit_price, qty))

    def subtotal(self) -> int:
        return sum(line.unit_price * line.qty for line in self.lines)
