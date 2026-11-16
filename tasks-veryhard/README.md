# Very hard eval tasks

The third task set. It is scored like `tasks-hard/` (a visible test, plus a
hidden test in `evals/hidden/veryhard/` that the agent never sees), and adds
three things that set doesn't test:

- **Rules given only as tests.** Task 01 doesn't state the pricing rules. The
  agent has to work them out from failing tests and write them down itself.
- **A rule that changes.** Task 03 teaches a 16:00 warehouse cut-off and task 04
  moves it to 14:00. Later tasks need the new one, so memory that still says
  16:00 fails them.
- **Several rules at once.** Each "similar" task needs two or three rules
  together.

| Group | Folders | What it tests |
|---|---|---|
| learn | 01-04 | Pricing rules from tests only, reference numbers, the dispatch cut-off, then the cut-off change. |
| similar | 05-07 | An invoice, a delivery date and a dispatch manifest. None of them states the rules it needs. |
| new | 08-09 | A coupon engine and bank reconciliation. Everything needed is in `TASK.md`. |
| different | 10-11 | A spreadsheet evaluator and a pattern matcher, with no store code. |

Run it with `scripts/run-evals.sh --suite veryhard`, or with `--rounds 6` for
the rounds experiment.

Every task was checked against a reference solution that passes both tests,
while the starting code fails them. For the "similar" tasks, a fix written
without the rules passes the visible test and fails the hidden one, and so does
a fix that uses the old 16:00 cut-off. The reference solutions aren't in this
repo.
