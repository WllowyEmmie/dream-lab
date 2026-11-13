# Touching intervals aren't merged

merge([(1, 2), (2, 3)]) returns both intervals. Intervals that touch should merge into (1, 3).

## Done when

- `python -m unittest` passes in this folder.
- You didn't edit `test_task.py`.
