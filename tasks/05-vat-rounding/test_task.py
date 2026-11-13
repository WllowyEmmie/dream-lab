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

    def test_vat_rounds_half_up(self):
        from shop import tax
        self.assertEqual(tax.vat(60), 5)       # 4.5 -> 5
        self.assertEqual(tax.vat(220), 17)     # 16.5 -> 17
        self.assertEqual(tax.vat(100), 8)      # 7.5 -> 8
        self.assertEqual(tax.vat(1000), 75)
