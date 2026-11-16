import unittest

from store.quotes import Quote


def quote(subtotal, handling_percent=0):
    q = Quote("Ade Stores", handling_percent=handling_percent)
    q.add("Item", subtotal)
    return q


class HiddenTest(unittest.TestCase):
    def test_exact_amounts_still_right(self):
        q = quote(20_000, 10)
        self.assertEqual((q.handling(), q.vat(), q.total()), (2_000, 1_500, 23_500))

    def test_vat_rounds_up_a_quarter(self):
        self.assertEqual(quote(110).vat(), 9)       # 8.25

    def test_vat_rounds_up_a_half(self):
        self.assertEqual(quote(60).vat(), 5)        # 4.5

    def test_vat_rounds_up_a_tiny_fraction(self):
        self.assertEqual(quote(1).vat(), 1)         # 0.075

    def test_handling_rounds_half_up(self):
        self.assertEqual(quote(25, 10).handling(), 3)    # 2.5
        self.assertEqual(quote(5, 10).handling(), 1)     # 0.5
        self.assertEqual(quote(104, 10).handling(), 10)  # 10.4

    def test_fractional_handling_percent(self):
        self.assertEqual(quote(1_000, 2.5).handling(), 25)

    def test_total_adds_up(self):
        q = quote(110, 10)
        self.assertEqual(q.total(), 110 + 11 + 9)
