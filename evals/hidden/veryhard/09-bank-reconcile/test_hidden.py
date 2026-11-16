import unittest
from datetime import date

from store.reconcile import reconcile


def L(id, amount, day, ref=None):
    return {"id": id, "amount": amount, "date": date(2026, 1, day), "ref": ref}


B = L


class HiddenTest(unittest.TestCase):
    def check(self, ledger, bank, matched, unmatched_ledger=(), unmatched_bank=()):
        self.assertEqual(reconcile(ledger, bank), {"matched": list(matched), "unmatched_ledger": list(unmatched_ledger),
                                                   "unmatched_bank": list(unmatched_bank)})

    def test_basic_still_works(self):
        self.check([L("L1", 5_000, 5, "INV-2026-000001"), L("L2", 7_500, 6)],
                   [B("B1", 7_500, 7), B("B2", 5_000, 20, "inv-2026-000001"), B("B3", 999, 7)],
                   [("L1", "B2"), ("L2", "B1")], unmatched_bank=["B3"])

    def test_reference_ignores_case_and_spaces_but_needs_the_amount(self):
        self.check([L("L1", 5_000, 5, " Ref-1 "), L("L2", 6_000, 5, "REF-2")],
                   [B("B1", 5_000, 25, "ref-1"), B("B2", 6_001, 5, "ref-2")],
                   [("L1", "B1")], ["L2"], ["B2"])

    def test_blank_references_do_not_match_each_other(self):
        self.check([L("L1", 5_000, 1, ""), L("L2", 5_000, 2, "  ")], [B("B1", 5_000, 20, ""), B("B2", 5_000, 21, None)],
                   [], ["L1", "L2"], ["B1", "B2"])

    def test_several_entries_with_the_same_reference(self):
        self.check([L("L2", 5_000, 9, "R"), L("L1", 5_000, 9, "R"), L("L3", 5_000, 3, "R")],
                   [B("B1", 5_000, 10, "R"), B("B2", 5_000, 11, "R")],
                   [("L1", "B2"), ("L3", "B1")], ["L2"])

    def test_reference_pass_runs_before_any_amount_match(self):
        # B1 comes first and could take L1 by amount, but B2 has L1's reference.
        self.check([L("L1", 5_000, 5, "R")], [B("B1", 5_000, 5), B("B2", 5_000, 6, "r")],
                   [("L1", "B2")], unmatched_bank=["B1"])

    def test_amount_window_is_three_days_either_side(self):
        self.check([L("L1", 100, 10), L("L2", 200, 10), L("L3", 300, 10), L("L4", 400, 10)],
                   [B("B1", 100, 13), B("B2", 200, 14), B("B3", 300, 7), B("B4", 400, 6)],
                   [("L1", "B1"), ("L3", "B3")], ["L2", "L4"], ["B2", "B4"])

    def test_closest_date_then_earliest_then_smallest_id(self):
        self.check([L("L1", 100, 8), L("L2", 100, 11), L("L3", 100, 9)], [B("B1", 100, 10)],
                   [("L3", "B1")], ["L1", "L2"])                      # L2 and L3 are both 1 day away; L3 is earlier
        self.check([L("L2", 100, 9), L("L1", 100, 9)], [B("B1", 100, 10)], [("L1", "B1")], ["L2"])

    def test_closest_date_wins_over_earliest(self):
        self.check([L("L1", 100, 7), L("L2", 100, 10)], [B("B1", 100, 10)], [("L2", "B1")], ["L1"])

    def test_bank_lines_are_taken_in_date_then_id_order(self):
        # Both bank lines want L1; the earlier one gets it, whatever order the list is in.
        self.check([L("L1", 100, 10)], [B("B2", 100, 11), B("B1", 100, 9)], [("L1", "B1")], unmatched_bank=["B2"])
        self.check([L("L1", 100, 10)], [B("B2", 100, 9), B("B1", 100, 9)], [("L1", "B1")], unmatched_bank=["B2"])

    def test_each_entry_matched_once(self):
        self.check([L("L1", 100, 10), L("L2", 100, 10)], [B("B1", 100, 10), B("B2", 100, 10), B("B3", 100, 10)],
                   [("L1", "B1"), ("L2", "B2")], unmatched_bank=["B3"])

    def test_reference_with_wrong_amount_can_still_match_by_amount(self):
        self.check([L("L1", 100, 10, "R"), L("L2", 150, 10)], [B("B1", 150, 11, "R")], [("L2", "B1")], ["L1"])

    def test_empty(self):
        self.check([], [], [])
        self.check([L("L1", 1, 1)], [], [], ["L1"])
