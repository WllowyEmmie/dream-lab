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

    def test_ties_alphabetical(self):
        from shop.orders import Orders
        from shop.reports import top_products
        self.catalog.add("CCC-3", "Ruler", "1.00", stock=10)
        self.catalog.add("BBB-2", "Eraser", "1.00", stock=10)
        orders = Orders(self.catalog)
        for sku, qty in [("CCC-3", 2), ("ABC-1", 2), ("BBB-2", 3)]:
            cart = Cart(self.catalog)
            cart.add(sku, qty)
            orders.place(cart)
        self.assertEqual(top_products(orders), ["BBB-2", "ABC-1", "CCC-3"])
