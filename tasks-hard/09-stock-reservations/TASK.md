# Hold stock while a customer checks out

Implement `Reservations` in `store/reservations.py`. It holds units for a
customer for a limited time while they check out.

`Reservations(stock, now)` takes the units on hand per SKU and a function that
returns the current time in seconds.

- `on_hand(sku)`: units physically in stock.
- `available(sku)`: units on hand minus units held by reservations that haven't
  expired. A reservation made at time `t` with `ttl` seconds has expired once
  `now() >= t + ttl`.
- `reserve(sku, qty, ttl)`: hold `qty` units for `ttl` seconds and return the
  reservation's id. Ids are `"R1"`, `"R2"`, ... in the order reservations
  succeed; a failed call doesn't use up an id. Raises `ValueError` if `qty` or
  `ttl` isn't positive, and `OutOfStock` if fewer than `qty` units are available.
- `confirm(id)`: the sale went through. The units leave stock for good and the
  reservation is gone. Raises `NotFound` if the id is unknown, has expired, or
  was already confirmed or released.
- `release(id)`: the customer gave up, so the units become available again.
  Releasing an id that is unknown, expired or already used does nothing.

`on_hand`, `available` and `reserve` raise `NotFound` for a SKU that isn't in
stock at all. Check for an unknown SKU before anything else.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
