# Refunds go back to the wrong tender

An order can be paid with several tenders: card, cash and gift card.
`Payment.refund` in `store/refunds.py` decides how a refund is split between
them, and it gets it wrong. A customer who paid ₦30 by gift card and ₦50 by
card asked for ₦40 back and got ₦30 of it on the gift card.

How refunds must work:

- Refunds go back to **card first, then cash, then gift card**.
- A tender never gets back more than was paid with it, counting everything
  already refunded to it by earlier refunds.
- `refund(amount)` returns a dict of tender to amount, with only the tenders
  that got something back.
- Refunding more than `refundable()` raises `ValueError` and changes nothing.
- `amount` must be positive, or `ValueError`.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
