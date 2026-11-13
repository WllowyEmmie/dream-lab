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

    def test_lookup_any_spelling(self):
        from shop.orders import Orders
        orders = Orders(self.catalog)
        cart = Cart(self.catalog)
        cart.add("ABC-1")
        placed = orders.place(cart)
        self.assertIs(orders.get("ord-0001"), placed)
        self.assertEqual(orders.cancel(" ORD-0001 ").status, "cancelled")
