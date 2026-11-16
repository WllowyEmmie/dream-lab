import unittest

from store.coupons import best_coupons


class TaskTest(unittest.TestCase):
    def test_percent_and_fixed_stack(self):
        coupons = [{"code": "P10", "kind": "percent", "value": 10}, {"code": "F500", "kind": "fixed", "value": 500}]
        self.assertEqual(best_coupons(10_000, coupons), (["F500", "P10"], 1_500))

    def test_no_coupons(self):
        self.assertEqual(best_coupons(10_000, []), ([], 0))
