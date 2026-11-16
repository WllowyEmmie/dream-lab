# Value stock first-in, first-out

Finance wants stock valued first-in, first-out (FIFO). Implement `Inventory`
in `store/inventory.py`. Costs are whole kobo.

- `receive(qty, unit_cost)`: a delivery of `qty` units that cost `unit_cost`
  each. Each delivery is its own layer, even when the cost matches the previous
  one. Raises `ValueError` if `qty` isn't positive or `unit_cost` is negative.
- `ship(qty)`: take `qty` units out, oldest layers first, and return what those
  units cost in total. Raises `ValueError` if `qty` isn't positive, and
  `OutOfStock` if there aren't enough units, in which case nothing changes.
- `units()`: units in stock.
- `value()`: what the units in stock cost.
- `layers()`: the remaining layers, oldest first, as `(qty, unit_cost)` tuples.
  Used-up layers aren't listed.
- `average_cost()`: `value()` divided by `units()`, rounded half up to a whole
  kobo. Returns 0 when there is no stock.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
