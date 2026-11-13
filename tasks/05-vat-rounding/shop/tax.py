from . import money

VAT_BPS = 750  # 7.5% VAT, in basis points


def vat(amount: int) -> int:
    """VAT on an amount in kobo, rounded half up to a whole kobo."""
    return round(amount * VAT_BPS / 10000)
