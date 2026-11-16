# Build invoices for orders

Finance needs an invoice for every order. Implement
`make_invoice(order_ref, lines)` in `store/invoices.py`.

The invoice for order `ORD-2026-000123` has the reference `INV-2026-000123`:
the same year and number with the `INV` prefix.

Return a dict with:

- `order_ref` and `invoice_ref`
- `lines`: a list of `(name, amount)`, one per line, where amount is what that
  line costs before VAT
- `net`: the sum of the line amounts
- `vat`
- `total`: net plus VAT

All amounts are whole kobo.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
