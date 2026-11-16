# Find the next run of a cron schedule

Implement `next_run(expr, after)` in `cron.py`. `expr` is a five-field cron
expression and `after` is a naive `datetime`. Return the first matching minute
**strictly after** `after`, as a `datetime` with seconds set to zero. Seconds in
`after` are ignored: at 10:00:30, a schedule that runs at 10:00 has already run.

The five fields, separated by spaces: minute (0-59), hour (0-23), day of month
(1-31), month (1-12), day of week (0-7, where 0 and 7 are both Sunday and 1 is
Monday).

Each field is a comma-separated list of:

- `*`: every value
- a number: `5`
- a range: `1-5`
- a step, only after `*` or a range: `*/15`, `10-30/5`. The step starts from
  the first value of the range.

Day matching follows standard cron. When both day of month and day of week are
restricted, a day matches if **either** one matches. When only one is
restricted, that one decides. A field counts as unrestricted only when it is
exactly `*`.

Raise `ValueError` for anything invalid: the wrong number of fields, a value out
of range, a range that runs backwards, a zero step, a step after a single
number, an empty list item, anything that isn't a number. Also raise
`ValueError` if the schedule has no run in the 8 years after `after`, such as
`0 0 30 2 *`.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
