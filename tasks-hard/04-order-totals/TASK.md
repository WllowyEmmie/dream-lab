# Checkout totals are wrong

Customers and finance both report wrong totals from `store/totals.py`. These
are the store's rules for working out a total, in this order:

1. **Discount first.** A percent discount applies to every line, rounded half up
   per line.
2. **Then shipping.** Free shipping is decided on the subtotal *after* the
   discount: ₦50,000.00 or more ships free, anything less pays the flat
   ₦2,500.00.
3. **VAT last.** VAT is charged on goods after the discount, and never on
   shipping. Books and staple foods (categories `books` and `staples`) are
   VAT-exempt. VAT is worked out once, on the taxable amount as a whole.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
