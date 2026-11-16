import unittest

from store.errors import NotFound, OutOfStock
from store.reservations import Reservations


class Clock:
    def __init__(self):
        self.t = 1000

    def __call__(self):
        return self.t


class HiddenTest(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.res = Reservations({"PEN": 10, "INK": 2}, self.clock)

    def test_basic_flow_still_works(self):
        rid = self.res.reserve("PEN", 4, ttl=60)
        self.res.confirm(rid)
        self.assertEqual((self.res.on_hand("PEN"), self.res.available("PEN")), (6, 6))

    def test_expiry_boundary(self):
        self.res.reserve("PEN", 4, ttl=60)
        self.clock.t = 1059
        self.assertEqual(self.res.available("PEN"), 6)
        self.clock.t = 1060
        self.assertEqual(self.res.available("PEN"), 10)

    def test_expired_units_can_be_reserved_again(self):
        self.res.reserve("PEN", 10, ttl=60)
        self.clock.t = 1060
        self.assertEqual(self.res.reserve("PEN", 10, ttl=60), "R2")

    def test_confirm_expired_raises_and_keeps_stock(self):
        rid = self.res.reserve("PEN", 4, ttl=60)
        self.clock.t = 1060
        with self.assertRaises(NotFound):
            self.res.confirm(rid)
        self.assertEqual(self.res.on_hand("PEN"), 10)

    def test_confirm_twice_or_unknown(self):
        rid = self.res.reserve("PEN", 4, ttl=60)
        self.res.confirm(rid)
        with self.assertRaises(NotFound):
            self.res.confirm(rid)
        with self.assertRaises(NotFound):
            self.res.confirm("R99")
        self.assertEqual(self.res.on_hand("PEN"), 6)

    def test_release(self):
        rid = self.res.reserve("PEN", 4, ttl=60)
        self.res.release(rid)
        self.assertEqual(self.res.available("PEN"), 10)
        self.res.release(rid)             # again: nothing happens
        self.res.release("R99")           # unknown: nothing happens
        with self.assertRaises(NotFound):
            self.res.confirm(rid)
        self.assertEqual(self.res.on_hand("PEN"), 10)

    def test_ids_skip_nothing_after_failures(self):
        self.assertEqual(self.res.reserve("INK", 2, ttl=60), "R1")
        with self.assertRaises(OutOfStock):
            self.res.reserve("INK", 1, ttl=60)
        with self.assertRaises(ValueError):
            self.res.reserve("PEN", 0, ttl=60)
        with self.assertRaises(ValueError):
            self.res.reserve("PEN", 1, ttl=0)
        self.assertEqual(self.res.reserve("PEN", 1, ttl=60), "R2")

    def test_skus_are_separate(self):
        self.res.reserve("PEN", 10, ttl=60)
        self.assertEqual(self.res.available("INK"), 2)

    def test_unknown_sku(self):
        for call in (lambda: self.res.on_hand("NOPE"), lambda: self.res.available("NOPE"),
                     lambda: self.res.reserve("NOPE", 1, ttl=60), lambda: self.res.reserve("NOPE", 0, ttl=60)):
            with self.assertRaises(NotFound):
                call()
