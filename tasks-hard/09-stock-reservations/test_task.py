import unittest

from store.errors import OutOfStock
from store.reservations import Reservations


class Clock:
    def __init__(self):
        self.t = 1000

    def __call__(self):
        return self.t


class TaskTest(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.res = Reservations({"PEN": 10}, self.clock)

    def test_reserve_and_confirm(self):
        rid = self.res.reserve("PEN", 4, ttl=60)
        self.assertEqual(rid, "R1")
        self.assertEqual(self.res.available("PEN"), 6)
        self.assertEqual(self.res.on_hand("PEN"), 10)
        self.res.confirm(rid)
        self.assertEqual(self.res.on_hand("PEN"), 6)
        self.assertEqual(self.res.available("PEN"), 6)

    def test_cannot_reserve_more_than_available(self):
        self.res.reserve("PEN", 8, ttl=60)
        with self.assertRaises(OutOfStock):
            self.res.reserve("PEN", 3, ttl=60)
