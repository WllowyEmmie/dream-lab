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

    def test_remove_with_different_spelling(self):
        cart = Cart(self.catalog)
        cart.add("abc-1", 2)
        cart.remove("abc-1")
        self.assertEqual(cart.lines, {"ABC-1": 1})
        cart.remove(" ABC-1 ")
        self.assertEqual(cart.lines, {})
