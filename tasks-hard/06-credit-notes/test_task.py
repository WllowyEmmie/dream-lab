import unittest

from store.credit_notes import CreditNotes
from store.errors import NotFound


class TaskTest(unittest.TestCase):
    def test_issue_and_get(self):
        notes = CreditNotes()
        notes.issue("CRN-2026-000042", 5_000)
        notes.issue("CRN-2026-000007", 1_200)
        self.assertEqual(notes.get("CRN-2026-000042"), 5_000)
        self.assertEqual(notes.refs(), ["CRN-2026-000007", "CRN-2026-000042"])

    def test_unknown_note(self):
        with self.assertRaises(NotFound):
            CreditNotes().get("CRN-2026-000099")

    def test_duplicate(self):
        notes = CreditNotes()
        notes.issue("CRN-2026-000042", 5_000)
        with self.assertRaises(ValueError):
            notes.issue("CRN-2026-000042", 1)
