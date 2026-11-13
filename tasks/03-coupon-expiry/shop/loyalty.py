from . import money

POINTS_BPS = 250   # customers earn 2.5% of what they paid, as points (1 point = 1 kobo)


def points_for(order) -> int:
    """Loyalty points for an order: 2.5% of the net amount paid, rounded half up."""
    if order.status != "placed":
        return 0
    return money.apply_bps(order.total - order.refunded, POINTS_BPS)
