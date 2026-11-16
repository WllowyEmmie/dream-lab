import unittest

from store.totals import Line, totals


class TaskTest(unittest.TestCase):
    def test_vat_not_charged_on_shipping(self):
        self.assertEqual(totals([Line("Radio", "electronics", 1_000_000)]),
                         {"subtotal": 1_000_000, "discount": 0, "shipping": 250_000, "vat": 75_000, "total": 1_325_000})

    def test_exempt_categories(self):
        result = totals([Line("Novel", "books", 400_000, 2), Line("Rice", "staples", 300_000)])
        self.assertEqual(result["vat"], 0)
        self.assertEqual(result["total"], 1_350_000)

    def test_free_shipping_decided_after_discount(self):
        result = totals([Line("TV", "electronics", 6_000_000)], discount_percent=20)
        self.assertEqual(result, {"subtotal": 6_000_000, "discount": 1_200_000, "shipping": 250_000,
                                  "vat": 360_000, "total": 5_410_000})

    def test_free_shipping_at_exactly_the_threshold(self):
        result = totals([Line("Fridge", "electronics", 5_000_000)])
        self.assertEqual(result["shipping"], 0)
        self.assertEqual(result["total"], 5_375_000)

    def test_discount_then_vat_on_taxable_lines_only(self):
        result = totals([Line("Lamp", "home", 200_000), Line("Novel", "books", 100_000)], discount_percent=10)
        self.assertEqual(result, {"subtotal": 300_000, "discount": 30_000, "shipping": 250_000,
                                  "vat": 13_500, "total": 533_500})

    def test_discount_rounds_half_up_per_line(self):
        result = totals([Line("Clip", "office", 5), Line("Pin", "office", 5)], discount_percent=10)
        self.assertEqual(result["discount"], 2)

    def test_vat_rounds_up(self):
        self.assertEqual(totals([Line("Pen", "office", 110)])["vat"], 9)
