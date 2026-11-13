# Orders can't be found by lower-case ID

Support staff type order IDs like "ord-0001" or paste " ORD-0001 " with spaces, and get NotFound. Cancelling by those IDs fails too.

## Done when

- `python -m unittest` passes in this folder.
- You didn't edit `test_task.py`.
