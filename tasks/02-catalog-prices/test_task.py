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

    def test_prices_stored_exactly(self):
        self.assertEqual(self.catalog.add("P-1", "Mug", "19.99").price, 1999)
        self.assertEqual(self.catalog.add("P-2", "Cup", "0.29").price, 29)
        self.assertEqual(self.catalog.add("P-3", "Jug", "1150").price, 115000)
