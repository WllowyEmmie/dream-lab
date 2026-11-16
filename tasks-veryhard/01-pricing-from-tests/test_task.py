import unittest

from store.pricing import Line, basket_total, line_total, vat


class TaskTest(unittest.TestCase):
    def test_line_totals(self):
        self.assertEqual(line_total(Line("Pen", "office", 100, 9)), 900)
        self.assertEqual(line_total(Line("Pen", "office", 100, 10)), 950)
        self.assertEqual(line_total(Line("Pen", "office", 100, 20)), 1900)
        self.assertEqual(line_total(Line("Radio", "electronics", 1_000_000)), 1_000_000)

    def test_small_bulk_lines(self):
        self.assertEqual(line_total(Line("Clip", "office", 5, 10)), 47)
        self.assertEqual(line_total(Line("Tag", "office", 3, 10)), 28)
        self.assertEqual(line_total(Line("Pin", "office", 1, 10)), 9)

    def test_vat(self):
        self.assertEqual(vat([Line("Radio", "electronics", 1_000_000)]), 75_000)
        self.assertEqual(vat([Line("Pen", "office", 110)]), 9)
        self.assertEqual(vat([Line("Cap", "office", 60)]), 5)
        self.assertEqual(vat([Line("Dot", "office", 1)]), 1)

    def test_vat_by_category(self):
        self.assertEqual(vat([Line("Novel", "books", 400_000), Line("Rice", "staples", 300_000)]), 0)
        self.assertEqual(vat([Line("Novel", "books", 1_000), Line("Lamp", "home", 1_000)]), 75)

    def test_vat_on_a_bulk_line(self):
        self.assertEqual(vat([Line("Pen", "office", 100, 10)]), 72)

    def test_basket(self):
        self.assertEqual(basket_total([Line("Pen", "office", 100, 10), Line("Novel", "books", 500)]), 1522)
