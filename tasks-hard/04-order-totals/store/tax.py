"""Tax and rounding."""
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP

VAT_RATE_PERCENT = Decimal("7.5")


def half_up(value) -> int:
    """Round to a whole kobo, .5 going up."""
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def vat(amount: int) -> int:
    """VAT on an amount in kobo, always rounded up to the next kobo."""
    return int((Decimal(amount) * VAT_RATE_PERCENT / 100).to_integral_value(rounding=ROUND_CEILING))
