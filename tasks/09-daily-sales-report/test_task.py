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

    def test_todays_sales(self):
        from shop.orders import Orders
        from shop.reports import daily_sales
        orders = Orders(self.catalog)
        cart = Cart(self.catalog)
        cart.add("XYZ-9", 4)                    # ₦10.00
        order = orders.place(cart)
        self.assertEqual(daily_sales(orders), order.total)
        self.assertEqual(daily_sales(orders, date(2026, 1, 6)), 0)
