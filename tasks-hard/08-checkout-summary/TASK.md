# Build the checkout summary

The new checkout page needs a summary of what the customer will pay. Implement
`summary(items, discount_percent)` in `store/checkout.py`. It returns a dict
with `subtotal`, `discount`, `shipping`, `vat` and `total`, all in kobo.

- `discount_percent` is a percent discount on the order.
- Shipping is a flat ₦2,500.00, unless the order qualifies for free shipping
  (₦50,000.00 or more).
- VAT is 7.5%.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
