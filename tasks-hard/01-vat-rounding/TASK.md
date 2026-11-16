# VAT and service charges round the wrong way

Finance flagged two rounding problems in `store/tax.py`. They explained the
store's rounding rules, which apply everywhere money is calculated:

- Money is always a whole number of kobo.
- **VAT (7.5%) is always rounded up** to the next kobo, even when it is only a
  fraction over. The tax office never accepts under-collection.
- **Every other amount** (fees, charges, discounts) **rounds half up**: .5 goes up.

Python's `round()` does neither of these.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
