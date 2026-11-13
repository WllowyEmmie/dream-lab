# Unknown products crash with a confusing error

Looking up an SKU that doesn't exist gives None, and adding it to a cart crashes with AttributeError. It should raise the shop's NotFound error.

## Done when

- `python -m unittest` passes in this folder.
- You didn't edit `test_task.py`.
