# The pricing tests fail

The tests in `test_task.py` fail against `store/pricing.py`.

Finance wrote those tests straight from the store's pricing rules. Nobody has
the rules written down anywhere else, so the tests are the only description of
them. Work out the rules from the tests and make them pass.

These rules apply to every price the store calculates, so they will matter
again in later work.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
