import unittest

from store.coupons import best_coupons


def P(code, value, **more):
    return {"code": code, "kind": "percent", "value": value, **more}


def F(code, value, **more):
    return {"code": code, "kind": "fixed", "value": value, **more}


class HiddenTest(unittest.TestCase):
    def test_stacking_still_works(self):
        self.assertEqual(best_coupons(10_000, [P("P10", 10), F("F500", 500)]), (["F500", "P10"], 1_500))

    def test_only_one_percent_coupon(self):
        self.assertEqual(best_coupons(10_000, [P("P10", 10), P("P20", 20), F("F500", 500)]), (["F500", "P20"], 2_500))

    def test_one_coupon_per_group(self):
        coupons = [F("A1", 500, group="a"), F("A2", 900, group="a"), F("B1", 300, group="b"), F("N", 100)]
        self.assertEqual(best_coupons(10_000, coupons), (["A2", "B1", "N"], 1_300))

    def test_group_can_cost_the_best_percent(self):
        coupons = [P("P20", 20, group="a"), F("F3000", 3_000, group="a"), P("P10", 10)]
        self.assertEqual(best_coupons(10_000, coupons), (["F3000", "P10"], 4_000))

    def test_min_spend(self):
        coupons = [F("BIG", 5_000, min_spend=20_000), F("SMALL", 500)]
        self.assertEqual(best_coupons(19_999, coupons), (["SMALL"], 500))
        self.assertEqual(best_coupons(20_000, coupons), (["BIG", "SMALL"], 5_500))

    def test_nothing_usable(self):
        self.assertEqual(best_coupons(1_000, [F("BIG", 500, min_spend=2_000)]), ([], 0))

    def test_discount_is_capped_at_the_subtotal(self):
        self.assertEqual(best_coupons(1_000, [F("F800", 800), F("F700", 700)]), (["F700", "F800"], 1_000))

    def test_tie_prefers_fewer_coupons(self):
        self.assertEqual(best_coupons(1_000, [F("F1000", 1_000), F("F500", 500)]), (["F1000"], 1_000))
        self.assertEqual(best_coupons(1_000, [F("ZERO", 0), F("F500", 500)]), (["F500"], 500))
        self.assertEqual(best_coupons(0, [F("F500", 500)]), ([], 0))

    def test_tie_prefers_the_first_list_of_codes(self):
        self.assertEqual(best_coupons(10_000, [F("B5", 500, group="x"), F("A5", 500, group="x")]), (["A5"], 500))
        coupons = [F("B", 500, group="x"), F("C", 500, group="y"), F("A", 500, group="x"), F("Z", 500, group="y")]
        self.assertEqual(best_coupons(10_000, coupons), (["A", "C"], 1_000))

    def test_percent_rounds_half_up(self):
        self.assertEqual(best_coupons(25, [P("P10", 10)]), (["P10"], 3))
        self.assertEqual(best_coupons(104, [P("P10", 10)]), (["P10"], 10))

    def test_many_coupons(self):
        coupons = [P("P5", 5), P("P15", 15, min_spend=50_000), P("P12", 12, group="g1"), F("F1", 1_000, group="g1"),
                   F("F2", 2_000, group="g2"), F("F3", 2_500, group="g2", min_spend=40_000), F("F4", 300),
                   F("F5", 300), F("F6", 50, group="g3"), F("F7", 60, group="g3")]
        self.assertEqual(best_coupons(30_000, coupons), (["F2", "F4", "F5", "F7", "P12"], 6_260))

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            best_coupons(10_000, [F("X", 100), P("X", 10)])
        with self.assertRaises(ValueError):
            best_coupons(10_000, [{"code": "B", "kind": "bogo", "value": 1}])
        with self.assertRaises(ValueError):
            best_coupons(10, [{"code": "B", "kind": "bogo", "value": 1, "min_spend": 1_000}])
