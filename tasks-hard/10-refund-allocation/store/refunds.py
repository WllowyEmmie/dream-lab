"""Refunds for orders paid with more than one tender."""

PRIORITY = ["card", "cash", "gift_card"]     # refunds go back in this order


class Payment:
    def __init__(self, tenders):
        """tenders: list of (kind, amount in kobo), e.g. [("card", 5000), ("gift_card", 3000)]."""
        self.paid = {}
        for kind, amount in tenders:
            self.paid[kind] = self.paid.get(kind, 0) + amount
        self.refunded = {kind: 0 for kind in self.paid}

    def refundable(self) -> int:
        return sum(self.paid.values()) - sum(self.refunded.values())

    def refund(self, amount: int) -> dict:
        """Refund an amount and return how much went back to each tender."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        result = {}
        left = amount
        for kind in self.paid:
            part = min(left, self.paid[kind])
            self.refunded[kind] += part
            result[kind] = part
            left -= part
        if left > 0:
            raise ValueError("more than was paid")
        return result
