"""The shop's clock.

Always get the current time from clock.now(), never datetime.now() or
date.today(): tests freeze the clock with clock.freeze(). Times are UTC.
"""
from datetime import datetime, timezone

_frozen = None


def now() -> datetime:
    return _frozen if _frozen is not None else datetime.now(timezone.utc)


def freeze(at) -> None:
    global _frozen
    _frozen = at


def unfreeze() -> None:
    freeze(None)
