# dream-lab

This repo tests how memory and dreaming change a coding agent's results.
Eval tasks live in `tasks/`: each is broken code with a failing test.

## Subagents

- After changing code, run `git diff` and the task's test yourself, then ask
  `code-reviewer` to review, pasting both outputs into the request. Reviewers are
  read-only: they can read files but can't run commands.
- Give anything it reports to `fixer`, then ask `code-reviewer` again.
  Repeat until it reports nothing. You run this loop: subagents can't call each other.

## Git and GitHub

- For cloning, creating repos, pushing and pull requests, use the `github-workflow` skill.
- Push, create repos or open PRs only when the user asks for it in this session.
- Clone other repos next to dream-lab, never inside it. Work on an `agent/<task>` branch.
- Never force-push, push to `main` of an existing repo, merge PRs, or delete branches or repos.

## Finishing a task

- A task is done when its test passes and `code-reviewer` reports nothing.
