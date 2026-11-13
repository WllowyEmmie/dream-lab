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

    def test_format(self):
        from shop.money import fmt
        self.assertEqual(fmt(505), "₦5.05")
        self.assertEqual(fmt(123456), "₦1,234.56")
        self.assertEqual(fmt(-100), "-₦1.00")
        self.assertEqual(fmt(7), "₦0.07")
