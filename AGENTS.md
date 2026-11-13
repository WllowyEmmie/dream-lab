# dream-lab

This repo tests how memory and dreaming change a coding agent's results.
Eval tasks live in `tasks/`: each is broken code with a failing test.

## Memory

- At the start of every task, read `memory/INDEX.md`. Open only the memory files
  the index says are relevant to this task. If none are, open none.
- Memory is advice, not truth. If a note contradicts the code or a test, trust the
  code, and record the contradiction with the `record-mistake` skill.
- Never edit `memory/conventions.md`, `memory/past-mistakes.md` or `memory/INDEX.md`.
  The only memory file you write to is `memory/inbox.md`, by appending.
  The nightly dreaming pass sorts the inbox into the other files.

## Subagents

- After changing code, ask `code-reviewer` to review the change.
- Give anything it reports to `fixer`, then ask `code-reviewer` again.
  Repeat until it reports nothing. You run this loop: subagents can't call each other.
- `memory-reviewer` is only for reviewing dreaming diffs, not task code.

## Git and GitHub

- For cloning, creating repos, pushing and pull requests, use the `github-workflow` skill.
- Push, create repos or open PRs only when the user asks for it in this session.
- Clone other repos next to dream-lab, never inside it. Work on an `agent/<task>` branch.
- Never force-push, push to `main` of an existing repo, merge PRs, or delete branches or repos.

## Finishing a task

- A task is done when its test passes and `code-reviewer` reports nothing.
- Before finishing, append anything reusable you learned to `memory/inbox.md`.
