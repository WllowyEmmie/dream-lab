import unittest
from datetime import date

from store.reconcile import reconcile


class TaskTest(unittest.TestCase):
    def test_reference_then_amount(self):
        ledger = [{"id": "L1", "amount": 5_000, "date": date(2026, 1, 5), "ref": "INV-2026-000001"},
                  {"id": "L2", "amount": 7_500, "date": date(2026, 1, 6), "ref": None}]
        bank = [{"id": "B1", "amount": 7_500, "date": date(2026, 1, 7), "ref": None},
                {"id": "B2", "amount": 5_000, "date": date(2026, 1, 20), "ref": "inv-2026-000001"},
                {"id": "B3", "amount": 999, "date": date(2026, 1, 7), "ref": None}]
        self.assertEqual(reconcile(ledger, bank), {"matched": [("L1", "B2"), ("L2", "B1")],
                                                   "unmatched_ledger": [], "unmatched_bank": ["B3"]})
