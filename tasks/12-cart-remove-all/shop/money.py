"""Money helpers.

All money in this codebase is an int number of kobo (100 kobo = 1 naira).
Never store or compute money as a float.
"""
from decimal import Decimal, ROUND_HALF_UP


def to_kobo(naira) -> int:
    """Convert a naira amount ("19.99", 19 or a Decimal) to kobo. Pass strings, not floats."""
    return round_half_up(Decimal(str(naira)) * 100)


def round_half_up(value) -> int:
    """Round to a whole kobo, with .5 always going up.

    Don't use round(): it rounds .5 to the nearest even number.
    """
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def apply_bps(amount: int, bps: int) -> int:
    """Return bps basis points of amount (1500 bps = 15%), rounded half up."""
    return round_half_up(Decimal(amount) * bps / 10000)


def fmt(kobo: int) -> str:
    """Format kobo for display: 123456 -> "₦1,234.56"."""
    sign = "-" if kobo < 0 else ""
    naira, rest = divmod(abs(kobo), 100)
    return f"{sign}₦{naira:,}.{rest:02d}"
