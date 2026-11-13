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

    def test_buy_exact_stock(self):
        from shop.orders import Orders
        self.catalog.get("ABC-1").stock = 2
        cart = Cart(self.catalog)
        cart.add("ABC-1", 2)
        Orders(self.catalog).place(cart)
        self.assertEqual(self.catalog.get("ABC-1").stock, 0)

    def test_too_many_still_rejected(self):
        from shop.errors import OutOfStock
        from shop.orders import Orders
        self.catalog.get("ABC-1").stock = 2
        cart = Cart(self.catalog)
        cart.add("ABC-1", 3)
        with self.assertRaises(OutOfStock):
            Orders(self.catalog).place(cart)
        self.assertEqual(self.catalog.get("ABC-1").stock, 2)
