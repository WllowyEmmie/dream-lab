import unittest

from store.checkout import Item, summary


class TaskTest(unittest.TestCase):
    def test_small_order(self):
        self.assertEqual(summary([Item("Radio", "electronics", 1_000_000)]),
                         {"subtotal": 1_000_000, "discount": 0, "shipping": 250_000, "vat": 75_000, "total": 1_325_000})

    def test_large_order_ships_free(self):
        result = summary([Item("Fridge", "electronics", 6_000_000)])
        self.assertEqual(result["shipping"], 0)
        self.assertEqual(result["total"], 6_450_000)

    def test_discount(self):
        result = summary([Item("Radio", "electronics", 1_000_000)], discount_percent=10)
        self.assertEqual(result, {"subtotal": 1_000_000, "discount": 100_000, "shipping": 250_000,
                                  "vat": 67_500, "total": 1_217_500})
