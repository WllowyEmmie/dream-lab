from dataclasses import dataclass
from datetime import datetime

from . import clock


@dataclass
class Coupon:
    code: str
    bps: int                 # discount in basis points: 1500 = 15%
    expires_at: datetime     # UTC
    min_subtotal: int = 0    # kobo

    def is_valid(self, subtotal: int) -> bool:
        return clock.now() < self.expires_at and subtotal >= self.min_subtotal
