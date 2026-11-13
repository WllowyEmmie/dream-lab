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

    def test_get_unknown_raises(self):
        from shop.errors import NotFound
        with self.assertRaises(NotFound):
            self.catalog.get("NOPE-1")

    def test_add_unknown_to_cart_raises(self):
        from shop.errors import NotFound
        with self.assertRaises(NotFound):
            Cart(self.catalog).add("NOPE-1")
