import unittest

from store.errors import BadReference
from store.invoices import Line, make_invoice


class HiddenTest(unittest.TestCase):
    def test_single_line_still_right(self):
        invoice = make_invoice("ORD-2026-000123", [Line("Radio", "electronics", 1_000_000)])
        self.assertEqual((invoice["invoice_ref"], invoice["net"], invoice["vat"], invoice["total"]),
                         ("INV-2026-000123", 1_000_000, 75_000, 1_075_000))

    def test_typed_reference_is_put_in_stored_form(self):
        invoice = make_invoice(" ord-2026-123 ", [Line("Radio", "electronics", 1_000)])
        self.assertEqual(invoice["order_ref"], "ORD-2026-000123")
        self.assertEqual(invoice["invoice_ref"], "INV-2026-000123")

    def test_malformed_reference(self):
        for bad in ["ORD-26-123", "order 123", ""]:
            with self.subTest(bad=bad):
                with self.assertRaises(BadReference):
                    make_invoice(bad, [Line("Radio", "electronics", 1_000)])

    def test_bulk_line(self):
        invoice = make_invoice("ORD-2026-000001", [Line("Pen", "office", 100, 10), Line("Pad", "office", 100, 9)])
        self.assertEqual(invoice["lines"], [("Pen", 950), ("Pad", 900)])
        self.assertEqual(invoice["net"], 1_850)

    def test_bulk_discount_rounds_half_up(self):
        invoice = make_invoice("ORD-2026-000001", [Line("Clip", "office", 5, 10)])
        self.assertEqual(invoice["lines"], [("Clip", 47)])

    def test_exempt_categories(self):
        invoice = make_invoice("ORD-2026-000001", [Line("Novel", "books", 400_000), Line("Rice", "staples", 300_000)])
        self.assertEqual((invoice["vat"], invoice["total"]), (0, 700_000))

    def test_vat_rounds_up(self):
        self.assertEqual(make_invoice("ORD-2026-000001", [Line("Pen", "office", 110)])["vat"], 9)

    def test_vat_on_discounted_taxable_lines_only(self):
        invoice = make_invoice("ORD-2026-000001", [Line("Pen", "office", 100, 10), Line("Novel", "books", 500)])
        self.assertEqual((invoice["net"], invoice["vat"], invoice["total"]), (1_450, 72, 1_522))
