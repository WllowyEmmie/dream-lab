# Eval tasks

Each folder is one task: a `TASK.md` bug report, broken code, and a failing
`test_task.py`. A task is solved when `python -m unittest` passes in its folder
without changing `test_task.py`. Tests use only Python's standard library.

```
cd tasks/01-coupon-discount
python -m unittest
```

`tasks.json` lists every task with its group. The groups:

| Group | Folders | What it tests |
|---|---|---|
| learn | 01-06 | Run first. Each breaks one of the shop's house rules, so memory has something to learn. |
| similar | 07-11 | The same house rule broken somewhere else (`similar_to` names the learning task). Memory should help most here. |
| new | 12-16 | Ordinary bugs in the shop code that no house rule covers. |
| different | 17-21 | Standalone code with no shop. Memory should stay out of the way. |

Tasks 01-16 each contain their own copy of a small `shop/` package, so fixing
one task never changes another. Its house rules are written in the module
docstrings (`money.py`, `clock.py`, `ids.py`, `errors.py`).

Each task starts from a clean copy, so restore a folder after a run, for
example `git checkout -- tasks/` and `git clean -fd tasks/`.
