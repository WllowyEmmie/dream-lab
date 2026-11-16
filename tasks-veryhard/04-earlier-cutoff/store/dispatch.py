"""When an order leaves the warehouse."""
from datetime import date, datetime, timedelta, timezone

LAGOS = timezone(timedelta(hours=1))
CUTOFF_HOUR = 16


def is_working_day(day: date) -> bool:
    return day.weekday() != 6          # closed on Sunday


def next_working_day(day: date) -> date:
    day += timedelta(days=1)
    while not is_working_day(day):
        day += timedelta(days=1)
    return day


def dispatch_date(placed_at: datetime) -> date:
    """The day an order placed at this time is dispatched."""
    local = placed_at.astimezone(LAGOS)
    day = local.date()
    if not is_working_day(day) or local.hour >= CUTOFF_HOUR:
        return next_working_day(day)
    return day
