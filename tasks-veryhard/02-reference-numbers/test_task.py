import unittest

from store.errors import BadReference
from store.refs import canonical


class TaskTest(unittest.TestCase):
    def test_stored_form_unchanged(self):
        self.assertEqual(canonical("ORD-2026-000123"), "ORD-2026-000123")

    def test_typed_forms(self):
        self.assertEqual(canonical(" ord-2026-123 "), "ORD-2026-000123")
        self.assertEqual(canonical("inv-2025-7"), "INV-2025-000007")
        self.assertEqual(canonical("Crn-2026-000042"), "CRN-2026-000042")

    def test_bad_references(self):
        for bad in ["ORD-26-123", "ORD2026000123", "", "ORD-2026-1234567", "ORDER-2026-1", "ORD-2026-12a", "ORD-2026-"]:
            with self.subTest(bad=bad):
                with self.assertRaises(BadReference):
                    canonical(bad)
