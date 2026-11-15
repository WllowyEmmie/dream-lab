# Eval harness variants

`no-memory/` holds the files the "no memory" setup uses in place of the repo's
own: the same `AGENTS.md`, `code-reviewer` and `fixer`, with every memory rule
taken out. `scripts/run-evals.sh` copies them over a fresh workspace.

If you change `AGENTS.md` or the agents in `.pi/agents/`, make the same change
here, or the setups will differ by more than memory.
