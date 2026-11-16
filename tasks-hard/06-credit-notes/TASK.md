# Record credit notes and look them up

Support needs to record credit notes and look them up by reference. A credit
note reference looks like `CRN-2026-000042`.

Implement `issue`, `get` and `refs` in `store/credit_notes.py`:

- `issue(ref, amount)` records a credit note. Issuing the same reference twice
  raises `ValueError`.
- `get(ref)` returns the amount, or raises `NotFound` if there is no such note.
- `refs()` returns all references, sorted.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
