# Pick the best set of coupons

Customers can enter several coupon codes. Implement
`best_coupons(subtotal, coupons)` in `store/coupons.py`. It picks the
combination of coupons that saves the customer the most and returns
`(codes, discount)`: the chosen codes as a sorted list, and the discount in kobo.

`subtotal` is in kobo. Each coupon is a dict:

- `code`: a string, unique in the list
- `kind`: `"percent"` or `"fixed"`
- `value`: the percent, or the amount in kobo
- `min_spend` (optional, default 0): the coupon can only be used when
  `subtotal >= min_spend`
- `group` (optional): at most one coupon from each group can be used. Coupons
  without a group aren't limited this way.

Rules for a combination:

1. At most one percent coupon.
2. At most one coupon per group.
3. Its discount is the percent coupon's share of the subtotal, rounded half up,
   plus the value of every fixed coupon. The discount is capped at the subtotal.

Choosing:

- The biggest discount wins.
- On a tie, the combination with fewer coupons wins.
- If still tied, the one whose sorted list of codes comes first wins
  (comparing the lists, so `["A", "Z"]` beats `["B", "C"]`).
- Using no coupons at all is a combination too: `([], 0)`.

Raise `ValueError` if two coupons share a code or a coupon's kind isn't
`"percent"` or `"fixed"`, even if that coupon couldn't be used.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
