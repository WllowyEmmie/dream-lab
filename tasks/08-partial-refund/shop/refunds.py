from . import money
from .errors import ShopError


def refund(order, amount_naira=None) -> int:
    """Refund an order. amount_naira is a string like "5.50"; None refunds what's left.

    Returns the refunded amount in kobo.
    """
    if order.status != "placed":
        raise ShopError(f"{order.id} is {order.status}")
    left = order.total - order.refunded
    amount = left if amount_naira is None else int(float(amount_naira) * 100)
    if amount <= 0 or amount > left:
        raise ShopError("bad refund amount")
    order.refunded += amount
    return amount
