# Show an estimated delivery date

Customers want to see when their order should arrive. Implement
`estimate(placed_at, transit_days)` in `store/delivery.py`.

The order is dispatched from our warehouse, then the courier takes
`transit_days` working days to deliver it. The courier works the same days as
our warehouse. `placed_at` is a timezone-aware datetime, and the result is a
date.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
