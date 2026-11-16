import unittest

from store.credit_notes import CreditNotes
from store.errors import BadReference, NotFound


class HiddenTest(unittest.TestCase):
    def test_stored_form_still_works(self):
        notes = CreditNotes()
        notes.issue("CRN-2026-000042", 5_000)
        self.assertEqual(notes.get("CRN-2026-000042"), 5_000)
        with self.assertRaises(NotFound):
            notes.get("CRN-2026-000099")

    def test_lookup_in_lower_case_with_spaces(self):
        notes = CreditNotes()
        notes.issue("CRN-2026-000042", 5_000)
        self.assertEqual(notes.get("  crn-2026-000042 "), 5_000)

    def test_lookup_without_leading_zeros(self):
        notes = CreditNotes()
        notes.issue("CRN-2026-000042", 5_000)
        self.assertEqual(notes.get("CRN-2026-42"), 5_000)

    def test_issue_stores_the_stored_form(self):
        notes = CreditNotes()
        notes.issue(" crn-2026-7 ", 100)
        self.assertEqual(notes.refs(), ["CRN-2026-000007"])
        self.assertEqual(notes.get("CRN-2026-000007"), 100)

    def test_duplicate_in_another_spelling(self):
        notes = CreditNotes()
        notes.issue("crn-2026-7", 100)
        with self.assertRaises(ValueError):
            notes.issue("CRN-2026-000007", 200)

    def test_malformed_reference_on_issue(self):
        for bad in ["CRN-26-7", "CRN2026000007", "", "CRN-2026-1234567"]:
            with self.subTest(bad=bad):
                with self.assertRaises(BadReference):
                    CreditNotes().issue(bad, 100)

    def test_malformed_reference_on_get(self):
        with self.assertRaises(BadReference):
            CreditNotes().get("credit note 7")
