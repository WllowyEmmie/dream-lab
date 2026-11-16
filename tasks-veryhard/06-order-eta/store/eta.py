"""Delivery dates shown to customers."""
from datetime import date, datetime


def eta(placed_at: datetime, transit_days: int) -> date:
    """The day an order placed at this time should arrive.

    transit_days is how many working days the courier needs after dispatch.
    """
    raise NotImplementedError
