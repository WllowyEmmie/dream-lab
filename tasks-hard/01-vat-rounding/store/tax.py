"""Tax and charges on goods."""

VAT_RATE_PERCENT = 7.5


def vat(amount: int) -> int:
    """VAT on an amount in kobo."""
    return round(amount * VAT_RATE_PERCENT / 100)


def service_charge(amount: int, percent) -> int:
    """A percentage service charge on an amount in kobo."""
    return round(amount * percent / 100)
