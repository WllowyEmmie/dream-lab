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

    def test_remove_all_units(self):
        cart = Cart(self.catalog)
        cart.add("ABC-1", 2)
        cart.remove("ABC-1", 2)
        self.assertNotIn("ABC-1", cart.lines)

    def test_remove_some_units(self):
        cart = Cart(self.catalog)
        cart.add("ABC-1", 3)
        cart.remove("ABC-1", 2)
        self.assertEqual(cart.lines, {"ABC-1": 1})
