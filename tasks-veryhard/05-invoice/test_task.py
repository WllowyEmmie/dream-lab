import unittest

from store.invoices import Line, make_invoice


class TaskTest(unittest.TestCase):
    def test_single_line(self):
        self.assertEqual(make_invoice("ORD-2026-000123", [Line("Radio", "electronics", 1_000_000)]),
                         {"order_ref": "ORD-2026-000123", "invoice_ref": "INV-2026-000123",
                          "lines": [("Radio", 1_000_000)], "net": 1_000_000, "vat": 75_000, "total": 1_075_000})

    def test_two_lines(self):
        invoice = make_invoice("ORD-2025-000007", [Line("Lamp", "home", 20_000, 2), Line("Desk", "home", 60_000)])
        self.assertEqual(invoice["invoice_ref"], "INV-2025-000007")
        self.assertEqual(invoice["lines"], [("Lamp", 40_000), ("Desk", 60_000)])
        self.assertEqual((invoice["net"], invoice["vat"], invoice["total"]), (100_000, 7_500, 107_500))
