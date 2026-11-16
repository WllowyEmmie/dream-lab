from datetime import datetime


def next_run(expr: str, after: datetime) -> datetime:
    """The first minute strictly after `after` that matches the cron expression."""
    raise NotImplementedError
