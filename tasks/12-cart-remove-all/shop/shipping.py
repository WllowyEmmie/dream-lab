from . import money

# Fee by parcel weight, in kobo: up to 1 kg, up to 5 kg, then per extra kg.
UP_TO_1KG = 150_000
UP_TO_5KG = 300_000
PER_EXTRA_KG = 50_000


def fee(weight_g: int, member_bps: int = 0) -> int:
    """Shipping fee in kobo. Members get member_bps basis points off (1000 = 10%)."""
    if weight_g <= 1000:
        base = UP_TO_1KG
    elif weight_g <= 5000:
        base = UP_TO_5KG
    else:
        extra_kg = -(-(weight_g - 5000) // 1000)   # round up to whole kg
        base = UP_TO_5KG + extra_kg * PER_EXTRA_KG
    return base - money.apply_bps(base, member_bps)
