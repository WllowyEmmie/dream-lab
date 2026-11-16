---
name: run-evals
description: Use when the user asks, in any words, to run the eval tests or the experiment (easy, hard or very hard tasks; without memory, with memory, with memory and dreaming; in rounds), to check how far it has got, or to build the results report.
---
The eval experiment is run by `scripts/run-evals.sh`. It starts a separate Pi
run for every task, in its own folder outside this repo, and scores it. Your job
is to start that script, keep it going and report back. You don't do the eval
tasks yourself.

## What the user's words mean

| They say | Option |
|---|---|
| easy / hard / very hard tasks | `--suite easy`, `--suite hard`, `--suite veryhard` |
| without memory, no memory | `--setup none` |
| with memory, just memory | `--setup memory` |
| with dreaming, memory and dreaming | `--setup dreaming` |
| all three, compare them, nothing said | leave `--setup` out |
| rounds, round by round, "run it 6 times" | `--rounds 6` (use their number) |
| only the similar / new / different tasks | `--group similar` (not with `--rounds`) |
| one task | `--task <folder name>` |

If they don't say which task set, or whether they want rounds, ask once before
starting. Don't use `--manual`: it waits for a person.

## Running it

1. Check `git status`. Workspaces are built from the last commit, so if tasks,
   scripts or `.pi/` have uncommitted changes, tell the user and stop.
2. Run the script from the repo root in short pieces, with a 30 minute time
   limit on the command:
   `bash scripts/run-evals.sh <options> --max-runs 3`
3. Read the output. Each run prints a `PASS` or `FAIL` line with its turns and
   tokens. Tell the user in one or two lines what just ran and how it went.
4. If the last lines say `MORE:`, run the exact same command again. Keep going
   until they say `DONE:`.
5. If the output says Pi failed to run (a usage limit, an expired login), stop.
   Tell the user what it said, including any reset time. Finished runs are kept;
   the same command continues later. Don't retry in a loop.

## The report

When the user asks for results, or when everything is `DONE:`, run
`node scripts/build-report.mjs`. It writes `report.html` in the repo root. Tell
the user to open that file, and that it needs committing, because `dream.sh`
won't run while there are uncommitted files.

To say how far a run has got without running anything, build the report: its
first output line lists how many runs each task set has.

## Rules

- Never change a task, a test, a file under `evals/`, the runs files in
  `.dream-state/evals/` or `report.html` to alter a result. Don't open
  `evals/hidden/`.
- Don't write notes about eval runs to `memory/inbox.md`, and skip the
  code-review loop: running the script changes no code here.
- If a run looks wrong, say so and point at its folder (the script prints the
  work folder at the start). Don't fix it by hand.
