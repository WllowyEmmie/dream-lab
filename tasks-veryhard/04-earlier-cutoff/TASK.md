# The warehouse cut-off has moved

The warehouse has changed its cut-off. **From now on the cut-off is 14:00 Lagos
time, not 16:00.** An order placed at 14:00 or later leaves on the next working
day.

Nothing else about how the warehouse works has changed: it still works Monday
to Saturday, Lagos is still UTC+1, and timestamps are still UTC.

Update `store/dispatch.py`. The tests already expect the new cut-off. The old
16:00 cut-off is wrong everywhere from today, including in anything written
down about it.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
