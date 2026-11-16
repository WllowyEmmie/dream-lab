# Hard eval tasks

A second, harder task set. The first set (`tasks/`) turned out too easy: every
run passed with or without memory, so it couldn't show what memory changes.

What's different here, following how benchmarks like SWE-bench score work:

- **Hidden tests.** Each eval task has a visible `test_task.py` and a second
  test the agent never sees, kept in `evals/hidden/hard/`. A run only counts as
  passed when both pass. The visible test covers the basic case; the hidden one
  covers everything `TASK.md` asks for.
- **Rules that aren't in the code.** The learning tasks each explain one of the
  store's rules (how VAT rounds, how references are written, the warehouse
  cut-off, the order of discount, shipping and VAT). The "similar" tasks need
  those rules but don't mention them, and no code in their folder shows them.
  The only way to know them is to have learned them earlier.
- **Bigger tasks.** Most tasks ask for a whole feature, not a one-line fix.

| Group | Folders | What it tests |
|---|---|---|
| learn | 01-04 | Run first. Each explains one store rule, and its test enforces it. |
| similar | 05-08 | Needs a rule from a learning task (`needs` in `tasks.json`). Without it, a fix passes the visible test and fails the hidden one. |
| new | 09-11 | Harder work in the same store that needs no earlier rule. |
| different | 12-14 | Standalone problems: an expression evaluator, cron schedules, JSON Patch. |

Run a task's visible test with `python -m unittest test_task` in its folder.
Run the whole set with `scripts/run-evals.sh --suite hard`.

Every task was checked against a reference solution: it passes both tests, and
the starting code fails them. For the "similar" tasks, a plausible fix written
without the rule passes the visible test and fails the hidden one. The
reference solutions aren't in this repo.
