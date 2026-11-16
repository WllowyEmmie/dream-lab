# Quotes need handling, VAT and a total

Business customers need quotes that show a handling charge, VAT and a total.
Add three methods to `Quote` in `store/quotes.py`:

- `handling()`: the handling charge, which is `handling_percent` of the subtotal.
- `vat()`: VAT at 7.5% of the subtotal.
- `total()`: subtotal + handling + VAT.

All three return whole kobo.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
