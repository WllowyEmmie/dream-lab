from . import ids, money, tax
from .errors import InvalidCoupon, NotFound


class Cart:
    def __init__(self, catalog):
        self.catalog = catalog
        self.lines = {}        # sku -> quantity
        self.coupon = None

    def add(self, sku, qty=1):
        if qty <= 0:
            raise ValueError("qty must be positive")
        product = self.catalog.get(sku)
        self.lines[product.sku] = self.lines.get(product.sku, 0) + qty

    def remove(self, sku, qty=1):
        sku = ids.norm(sku)
        if sku not in self.lines:
            raise NotFound(sku)
        left = self.lines[sku] - qty
        if left < 0:
            del self.lines[sku]
        else:
            self.lines[sku] = left

    def subtotal(self) -> int:
        return sum(self.catalog.get(sku).price * qty for sku, qty in self.lines.items())

    def weight_g(self) -> int:
        return sum(self.catalog.get(sku).weight_g * qty for sku, qty in self.lines.items())

    def apply_coupon(self, coupon):
        if not coupon.is_valid(self.subtotal()):
            raise InvalidCoupon(coupon.code)
        self.coupon = coupon

    def discount(self) -> int:
        if self.coupon is None:
            return 0
        return money.apply_bps(self.subtotal(), self.coupon.bps)

    def total(self) -> int:
        after_discount = self.subtotal() - self.discount()
        return after_discount + tax.vat(after_discount)
