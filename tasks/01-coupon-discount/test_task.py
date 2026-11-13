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

    def test_fifteen_percent_coupon(self):
        from shop.coupons import Coupon
        cart = Cart(self.catalog)
        cart.add("ABC-1", 2)                       # ₦100.00
        cart.apply_coupon(Coupon("SAVE15", 1500, datetime(2026, 2, 1, tzinfo=timezone.utc)))
        self.assertEqual(cart.discount(), 1500)             # ₦15.00
        self.assertEqual(cart.total(), 8500 + 638)          # ₦85.00 + VAT

    def test_no_coupon(self):
        cart = Cart(self.catalog)
        cart.add("ABC-1")
        self.assertEqual(cart.discount(), 0)
