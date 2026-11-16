import unittest

from store.checkout import Item, summary


class HiddenTest(unittest.TestCase):
    def test_small_order_still_right(self):
        self.assertEqual(summary([Item("Radio", "electronics", 1_000_000)]),
                         {"subtotal": 1_000_000, "discount": 0, "shipping": 250_000, "vat": 75_000, "total": 1_325_000})

    def test_books_and_staples_are_vat_exempt(self):
        result = summary([Item("Novel", "books", 400_000, 2), Item("Rice", "staples", 300_000)])
        self.assertEqual(result["vat"], 0)
        self.assertEqual(result["total"], 1_350_000)

    def test_free_shipping_decided_after_discount(self):
        result = summary([Item("TV", "electronics", 6_000_000)], discount_percent=20)
        self.assertEqual(result["shipping"], 250_000)
        self.assertEqual(result["total"], 4_800_000 + 250_000 + 360_000)

    def test_free_shipping_at_exactly_the_threshold_after_discount(self):
        result = summary([Item("TV", "electronics", 6_250_000)], discount_percent=20)
        self.assertEqual(result["shipping"], 0)

    def test_vat_only_on_taxable_lines_after_discount(self):
        result = summary([Item("Lamp", "home", 200_000), Item("Novel", "books", 100_000)], discount_percent=10)
        self.assertEqual(result, {"subtotal": 300_000, "discount": 30_000, "shipping": 250_000,
                                  "vat": 13_500, "total": 533_500})

    def test_vat_rounds_up(self):
        self.assertEqual(summary([Item("Pen", "office", 110)])["vat"], 9)

    def test_discount_rounds_half_up_per_line(self):
        result = summary([Item("Clip", "office", 5), Item("Pin", "office", 5)], discount_percent=10)
        self.assertEqual(result["discount"], 2)
