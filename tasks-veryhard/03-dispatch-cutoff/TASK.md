# Dispatch dates are wrong

The warehouse says the dispatch dates from `store/dispatch.py` are often wrong.
This is how the warehouse works, and it applies to anything about dispatch or
delivery days:

- It works **Monday to Saturday**. Sunday is closed.
- The cut-off is **16:00 Lagos time** (UTC+1 all year, no daylight saving).
  An order placed before 16:00 on a working day leaves that day. An order placed
  at 16:00 or later, or on a Sunday, leaves on the next working day.
- Every timestamp in the store is in **UTC**, so convert to Lagos time first.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
