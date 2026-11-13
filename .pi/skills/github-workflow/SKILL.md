---
name: github-workflow
description: Use when the user asks to clone a GitHub repo, create a new repo, push a branch or open a pull request. Covers checking and logging in to the gh CLI.
---
Push, create a repo or open a PR only when the user asks for it in this session.

## 1. Check gh

Run `gh --version`.
- If it isn't found, ask the user before installing. If they agree, run
  `winget install --id GitHub.cli -e`, then tell them to restart the terminal
  (gh isn't on PATH until a new shell starts) and stop there.

## 2. Check login

Run `gh auth status`. If it says you're logged in, go to step 3.
Otherwise try the device login (this flow is untested):

1. Start it in the background, writing to a log file in the repo root:
   `gh auth login --web --hostname github.com --git-protocol https > .gh-login.log 2>&1 &`
2. Wait a few seconds, then read `.gh-login.log` and find the one-time code
   (looks like `ABCD-1234`).
3. Give the user the code and the link https://github.com/login/device.
   You may try to open the link for them, but always give it to them as text too.
4. Ask them to tell you when they've approved it. Then run `gh auth status`.
5. When it shows logged in, run `gh auth setup-git` so git uses gh for HTTPS.

If there's no code in the log, `gh auth status` still fails, or anything else
goes wrong: stop and ask the user to run `gh auth login` themselves, then
check `gh auth status` again.

## 3a. Working on an existing repo

1. Ask for the repo link.
2. Clone it next to dream-lab, never inside it:
   `gh repo clone <owner/repo or link> ../<repo-name>`
3. In the clone, make a branch named for the task: `git switch -c agent/<task>`.
   Do all work on that branch.

## 3b. Creating a new repo from this folder

1. Ask for the repo name and whether it should be public or private.
   Default to private if they don't say.
2. Make sure there's at least one commit, then run
   `gh repo create <name> --private --source=. --push` (or `--public`).

## 4. Opening a pull request

1. Push the branch: `git push -u origin agent/<task>`.
2. Create the PR: `gh pr create --base main --head agent/<task> --title "<title>" --body "<body>"`.
3. If the user gave a Linear issue, put `Fixes AI-<n>` on its own line in the body.
4. Give the user the PR link that gh prints.

## Never

- Force-push (`--force`, `--force-with-lease`, `+branch`).
- Push to `main` of an existing repo.
- Merge PRs.
- Delete branches or repos, locally or on GitHub.
