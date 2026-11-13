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

    def test_points_round_half_up(self):
        from shop.loyalty import points_for
        from shop.orders import Order
        when = clock.now()
        self.assertEqual(points_for(Order("ORD-1", {}, 100, when)), 3)    # 2.5 -> 3
        self.assertEqual(points_for(Order("ORD-2", {}, 500, when)), 13)   # 12.5 -> 13
        self.assertEqual(points_for(Order("ORD-3", {}, 400, when)), 10)
