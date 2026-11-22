# dream-lab

This repo tests how memory and dreaming change a coding agent's results.
Eval tasks live in `tasks/`: each is broken code with a failing test.

## Memory

- Before starting any task, read ALL of `memory/conventions.md`,
  `memory/past-mistakes.md` and `memory/inbox.md`. This is not optional, and they
  are short. Rules learned on earlier tasks are about this whole repo, not just the
  task they came from: they apply to every later task where they fit, even if the
  task and its test don't mention them.
- Follow a remembered rule unless the code or a test directly contradicts it. A test
  that doesn't check something is not a contradiction: keep following the rule.
- If a rule really is contradicted, trust the code, and record the contradiction
  with the `record-mistake` skill.
- Never edit `memory/conventions.md`, `memory/past-mistakes.md` or `memory/INDEX.md`.
  The only memory file you write to is `memory/inbox.md`, by appending.
  The nightly dreaming pass sorts the inbox into the other files.

## Subagents

- After changing code, run `git diff` and the task's test yourself, then ask
  `code-reviewer` to review, pasting both outputs into the request. Reviewers are
  read-only: they can read files but can't run commands.
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
- Before finishing, append anything reusable you learned to `memory/inbox.md`,
  using the `record-mistake` skill. Write each rule as a general fact about the
  repo, not as something that happened in this task.
