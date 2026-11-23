# dream-lab

Does memory help a coding agent, and does "dreaming" (a nightly pass that sorts and
trims that memory) make it worth the cost?

dream-lab tests this with the Pi coding agent (driven from T3 Code) on three sets of coding tasks, under three setups:

| Setup | What the agent has |
|---|---|
| **No memory** | Only the code. Every task starts from nothing. |
| **Memory** | A `memory/` folder. Agents add notes to `inbox.md`; nothing ever sorts them. |
| **Memory + dreaming** | The same, plus a dreaming pass between rounds that verifies, sorts and trims the notes. |

## Results

Six rounds: every setup does every task six times, and memory carries over from round
to round. "Similar" tasks need a house rule learned in an earlier task, without naming it.

| Model, set | Setup | All tasks | Similar | Cost* |
|---|---|---|---|---|
| Opus, hard | No memory | 60/84 | 0/24 | $17.95 |
| | Memory | 84/84 | 24/24 | $33.25 |
| | Memory + dreaming | 84/84 | 24/24 | $23.82 |
| Haiku, hard | No memory | 60/84 | 0/24 | $1.10 |
| | Memory | 81/84 | 24/24 | $2.34 |
| | Memory + dreaming | 84/84 | 24/24 | $1.64 |
| Haiku, very hard | No memory | 46/66 | 0/18 | $1.28 |
| | Memory | 61/66 | 13/18 | $1.65 |
| | Memory + dreaming | 64/66 | 17/18 | $1.55 |

\* API list-price estimates, including the dreaming passes. Haiku results use harness v2 (below).
The easy set passed every run in every setup, on both models.

What it shows:

- **Memory decides the rule-dependent tasks:** 0 of 24 without it, 24 of 24 with it.
- **Plain memory gets expensive:** notes grow every round (2k to 16k tokens), and tasks
  get slower and use more tokens.
- **Dreaming keeps memory near 2,000 tokens.** It was cheaper than plain memory and at
  least as accurate. On very hard, where a rule changes halfway (the cut-off moves
  from 16:00 to 14:00), it was clearly more accurate: plain memory kept both rules.
- **The harness matters on smaller models.** Under harness v1 Haiku had the right rules
  in memory but didn't apply them (0/8 on similar tasks). Harness v2 makes the agent
  read every memory file and treat remembered rules as repo-wide: 24/24.

Full charts and a per-task breakdown: `report.html` (rebuild with
`node scripts/build-report.mjs`).

## How it works

```
task -> Pi works, appends what it learned to memory/inbox.md
     -> (memory + dreaming) dream.sh: verify, organize, enrich, forget
     -> judge scores the memory diff -> merge if 4/5 or more
```

- `AGENTS.md`: rules for the agent. Read all of `memory/` before every task; append
  lessons with the `record-mistake` skill; never edit the sorted memory files directly.
- `memory/`: `INDEX.md`, `conventions.md` (sorted rules), `past-mistakes.md`,
  `inbox.md` (new notes, waiting for dreaming).
- `dream.sh` + `prompts/dream.md`: the dreaming pass. It works on its own branch and
  logs tokens and cost (`.dream-state/usage.csv`).
- Guardrails, enforced in the script:
  - **Scope check:** a pass that touches anything outside `memory/` isn't committed.
  - **Judge gate:** a read-only `memory-reviewer` scores accuracy, deduplication and
    scope; only 4 or more merges.
  - **Forgetting and a budget:** notes unused for 14 days are dropped, and memory must
    fit 2,000 tokens.
  - **Poison test:** `scripts/poison-test.sh` plants a wrong note and a stale note,
    runs a task and a dreaming pass on throwaway branches, and records whether
    dreaming caught them.
- Subagents (`.pi/agents/`): `code-reviewer` and `memory-reviewer` are read-only;
  `fixer` can edit.

## The evals

| Set | Tasks | Scored on | Tests mainly |
|---|---|---|---|
| Easy (`tasks/`) | 21 one-line bugs | the visible test | memory's overhead |
| Hard (`tasks-hard/`) | 14 whole features | visible + hidden tests | whether memory carries rules |
| Very hard (`tasks-veryhard/`) | 11 larger features | visible + hidden tests | whether dreaming fixes stale rules |

Each set has four groups, run in this order:

- **learn:** teaches a store rule, e.g. "VAT always rounds up to the next kobo".
- **similar:** needs that rule but never mentions it.
- **new:** same codebase, no rule needed.
- **different:** unrelated code.

**Hidden tests** (`evals/hidden/`) are copied in only after Pi finishes, as in
SWE-bench. A fix that ignores the rule usually passes the visible test but fails the
hidden ones. A run passes only if the visible test and every hidden test pass, and the
visible test wasn't edited.

## Running it

Requirements: Git Bash (on Windows), Node 22, Python 3, Pi 1.5.2. The `Dockerfile`
pins the versions used.

```bash
# Commit first: eval workspaces are built from HEAD, outside the repo (../dream-lab-evals).
scripts/run-evals.sh --suite hard --rounds 6               # all three setups
scripts/run-evals.sh --suite veryhard --rounds 6 --setup dreaming
scripts/run-evals.sh --suite hard --rounds 6 --model claude-haiku-5-5 --label harness-v2
scripts/run-evals.sh ... --max-runs 3                      # stop after 3 runs; rerun to continue

node scripts/build-report.mjs                              # rebuild report.html
REPORT_ONLY=claude-haiku-5-5-harness-v2 node scripts/build-report.mjs out.html   # one model only
```

Finished runs are skipped, so a run can stop (usage limit, Ctrl+C) and resume.

**In T3 Code:** ask Pi in plain text, e.g. *"On Haiku, with harness v2, run the hard
tasks in 6 rounds for all three setups"*. The `run-evals` skill turns that into the
command and keeps going until it's done.

**Dreaming on your own repo:**

```bash
./dream.sh                                  # one pass over today's sessions
scripts/schedule-dream.sh 2 0               # nightly at 02:00 (cron; macOS/Linux)
powershell -ExecutionPolicy Bypass -File scripts\schedule-dream.ps1   # 02:00 nightly (Windows)
```

**Slack:** copy `.env.example` to `.env` and set `SLACK_WEBHOOK_URL` to get a message
after each dreaming pass and eval round. `.env` is git-ignored.

## Limits

- Two models, a few tasks per group, list-price cost estimates.
- All tasks are about one e-commerce store's rules (money, references, dates).
  The hard sets test whether memory carries project rules, not general skill.
- The very hard set has only been run on Haiku.
- In the evals, every dreaming pass is merged whatever the judge scores; the score is
  only recorded.
