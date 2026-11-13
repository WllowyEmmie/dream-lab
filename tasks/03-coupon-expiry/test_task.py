import unittest
from datetime import date, datetime, timezone

from shop import clock
from shop.cart import Cart
from shop.catalog import Catalog


class TaskTest(unittest.TestCase):
    def setUp(self):
        clock.freeze(datetime(2026, 1, 5, 12, 0, tzinfo=timezone.utc))
        self.catalog = Catalog()
        self.catalog.add("ABC-1", "Notebook", "50.00", stock=10, weight_g=300)
        self.catalog.add("XYZ-9", "Pen", "2.50", stock=10, weight_g=20)

    def tearDown(self):
        clock.unfreeze()

    def test_coupon_valid_before_expiry(self):
        from shop.coupons import Coupon
        coupon = Coupon("NEWYEAR", 1000, datetime(2026, 2, 1, tzinfo=timezone.utc))
        self.assertTrue(coupon.is_valid(1000))

    def test_coupon_invalid_after_expiry(self):
        from shop.coupons import Coupon
        coupon = Coupon("NEWYEAR", 1000, datetime(2026, 2, 1, tzinfo=timezone.utc))
        clock.freeze(datetime(2026, 3, 1, tzinfo=timezone.utc))
        self.assertFalse(coupon.is_valid(1000))
