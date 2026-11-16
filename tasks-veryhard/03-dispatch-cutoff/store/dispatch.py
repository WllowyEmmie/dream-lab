"""When an order leaves the warehouse."""
from datetime import date, datetime


def dispatch_date(placed_at: datetime) -> date:
    """The day an order placed at this time is dispatched."""
    return placed_at.date()
