import unittest

from store.quotes import Quote


class TaskTest(unittest.TestCase):
    def test_quote(self):
        quote = Quote("Ade Stores", handling_percent=10)
        quote.add("Shelf", 10_000, 2)
        self.assertEqual(quote.handling(), 2_000)
        self.assertEqual(quote.vat(), 1_500)
        self.assertEqual(quote.total(), 23_500)

    def test_empty_quote(self):
        quote = Quote("Ade Stores")
        self.assertEqual((quote.handling(), quote.vat(), quote.total()), (0, 0, 0))
