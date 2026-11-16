# References typed by people aren't recognised

Support keeps failing to find orders because people type references in
different ways. `store/refs.py` should turn whatever a person typed into the
stored form. The rule covers every reference in the store (orders `ORD`,
invoices `INV`, credit notes `CRN`, and any other three-letter prefix):

- The stored form is `PREFIX-YYYY-NNNNNN`: three letters, a four-digit year and
  six digits, in upper case. Example: `ORD-2026-000123`.
- People type them in any case, with spaces around them, and often **without
  the leading zeros**: `ord-2026-123` means `ORD-2026-000123`.
- Always convert what a person typed to the stored form before storing it or
  looking it up.
- Anything that can't be converted raises `BadReference`. Never return `None`
  and never guess.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
