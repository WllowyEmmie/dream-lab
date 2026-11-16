# Match bank lines to ledger entries

Finance matches the bank statement against the ledger by hand. Implement
`reconcile(ledger, bank)` in `store/reconcile.py`.

Ledger entries and bank lines are dicts with `id` (a string), `amount` (kobo),
`date` (a `datetime.date`) and `ref` (a string or `None`). Each entry and each
line can be matched at most once.

Matching happens in two passes. In each pass, take the bank lines in order of
date, then id.

1. **Reference pass**, over every bank line. A bank line matches a ledger entry
   when both have a reference, the references are equal ignoring case and
   surrounding spaces, and the amounts are equal. An empty or blank reference
   counts as no reference. If several ledger entries qualify, take the one with
   the earliest date, then the smallest id.
2. **Amount pass**, over the bank lines still unmatched, using only ledger
   entries still unmatched. A bank line matches a ledger entry with the same
   amount whose date is at most 3 days before or after the bank line's date.
   If several qualify, take the one closest in date, then the earliest date,
   then the smallest id.

Return a dict with:

- `matched`: a list of `(ledger_id, bank_id)` pairs, sorted by ledger id
- `unmatched_ledger`: the ids of ledger entries left over, sorted
- `unmatched_bank`: the ids of bank lines left over, sorted

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
