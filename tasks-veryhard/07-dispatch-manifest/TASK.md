# List which orders leave on which day

The warehouse wants a manifest for each dispatch day: the orders that leave on
that day. Implement `build_manifests(orders)` in `store/manifest.py`.

`orders` is a list of `(order_ref, placed_at)` pairs, where `placed_at` is a
timezone-aware datetime. Return a dict that maps each dispatch date to the
sorted list of order references leaving that day. An order that is listed more
than once appears once.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
