#!/usr/bin/env bash
# Nightly dreaming pass for dream-lab (AI-13).
# Finds Pi sessions for this repo that haven't been dreamed over yet, runs Pi once
# with prompts/dream.md over them, and commits the memory/ changes on dreaming/DATE.
# Run from Git Bash in the dream-lab folder: ./dream.sh
set -euo pipefail

cd "$(dirname "$0")"
REPO_WIN="$(pwd -W 2>/dev/null || pwd)"           # C:/Users/... in Git Bash
SESSIONS_ROOT="${PI_CODING_AGENT_SESSION_DIR:-$HOME/.pi/agent/sessions}"
STATE_DIR=".dream-state"
PROCESSED="$STATE_DIR/processed.txt"
TODAY="$(date +%Y-%m-%d)"
BRANCH="dreaming/$TODAY"
BASE="${DREAM_BASE:-main}"
MERGE_AT="${DREAM_MERGE_THRESHOLD:-4}"   # auto-merge when the judge scores >= this (AI-17)
JUDGE_LOG="$STATE_DIR/judge-log.tsv"
BUDGET="${DREAM_MEMORY_BUDGET:-2000}"    # max tokens for all of memory/ (AI-18)
SIZE_LOG="$STATE_DIR/memory-size.tsv"

mkdir -p "$STATE_DIR"; touch "$PROCESSED"

# Rough size of memory/ in tokens: characters / 4. Not exact (real tokenizers
# differ), but steady enough to see whether memory grows or shrinks over time.
mem_tokens() { cat memory/*.md 2>/dev/null | wc -m | awk '{print int(($1 + 3) / 4)}'; }
mem_notes()  { cat memory/conventions.md memory/past-mistakes.md 2>/dev/null | grep -c '^- ' || true; }

# Settings that shouldn't be committed (like SLACK_WEBHOOK_URL) live in .env.
# tr strips Windows line endings, which would otherwise end up inside the values.
if [ -f .env ]; then
  set -a; . <(tr -d '\r' < .env); set +a
fi

# Post a message to Slack (AI-15). Does nothing if SLACK_WEBHOOK_URL isn't set.
# A failed post only prints a warning: it never stops the dreaming pass.
slack() {
  [ -n "${SLACK_WEBHOOK_URL:-}" ] || return 0
  local payload
  payload="$(node -e 'process.stdout.write(JSON.stringify({text: process.argv[1]}))' "$1")"
  curl -fsS -m 20 -X POST -H 'Content-Type: application/json' \
    --data "$payload" "$SLACK_WEBHOOK_URL" > /dev/null \
    || echo "Slack post failed; the dreaming result is unaffected." >&2
}

# Lowercase, forward slashes, no trailing slash: so C:\Users\X and c:/Users/X/ match.
norm() { printf '%s' "$1" | sed 's#\\\\#/#g; s#\\#/#g; s#/*$##' | tr '[:upper:]' '[:lower:]'; }
want="$(norm "$REPO_WIN")"

# 1. Find this repo's session files that aren't in the processed list.
#    The first line of each session file records the cwd Pi was started in.
new=()
while IFS= read -r -d '' f; do
  cwd="$(head -n 1 "$f" | grep -o '"cwd":"[^"]*"' | sed 's/^"cwd":"//; s/"$//' || true)"
  [ "$(norm "$cwd")" = "$want" ] || continue
  grep -qxF "$f" "$PROCESSED" && continue
  new+=("$f")
done < <(find "$SESSIONS_ROOT" -name '*.jsonl' -print0 2>/dev/null)

if [ ${#new[@]} -eq 0 ]; then
  echo "No new dream-lab sessions. Nothing to dream about."
  slack ":zzz: Dreaming $TODAY: no new sessions, nothing to dream about."
  exit 0
fi
echo "Dreaming over ${#new[@]} session(s)."

# 2. Refuse to start with uncommitted changes, so the commit holds only dreaming.
if [ -n "$(git status --porcelain)" ]; then
  echo "Working tree isn't clean. Commit or stash first." >&2
  exit 1
fi
START_BRANCH="$(git branch --show-current)"
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git switch -q "$BRANCH"       # second run on the same day adds to that branch
else
  git switch -q -c "$BRANCH" "$BASE"
fi

# 3. Run Pi once. --no-session: the dreaming run itself isn't saved, so it never
#    shows up as a "new session" next time.
list=""
for f in "${new[@]}"; do
  p="$(cygpath -m "$f" 2>/dev/null || printf '%s' "$f")"   # Windows path Pi can read
  list+="- $p"$'\n'
done
size_before="$(mem_tokens)"
pi -p --no-session @prompts/dream.md "TODAY: $TODAY
MEMORY_BUDGET: $BUDGET tokens
MEMORY_SIZE: $size_before tokens

Session transcripts to consolidate:
$list"

# 4. Only memory/ may change. Anything else: stop and leave it for a human.
outside="$(git status --porcelain | grep -v ' memory/' || true)"
if [ -n "$outside" ]; then
  echo "Dreaming changed files outside memory/. Not committing. Review these:" >&2
  echo "$outside" >&2
  slack ":warning: Dreaming $TODAY stopped: it changed files outside memory/. Nothing committed; left on \`$BRANCH\` for review.
\`\`\`$outside\`\`\`"
  exit 1
fi

if [ -n "$(git status --porcelain memory/)" ]; then
  git add memory/
  git commit -q -m "Dreaming pass $TODAY (${#new[@]} sessions)"
  echo "Committed on $BRANCH."
  stat="$(git show --stat --format= HEAD)"

  # Track memory size after every pass (AI-18). Over budget never auto-merges.
  size_after="$(mem_tokens)"
  [ -f "$SIZE_LOG" ] || printf 'date\tcommit\ttokens_before\ttokens_after\tnotes\tbudget\n' > "$SIZE_LOG"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$TODAY" "$(git rev-parse --short HEAD)" \
    "$size_before" "$size_after" "$(mem_notes)" "$BUDGET" >> "$SIZE_LOG"
  over_budget="no"; [ "$size_after" -le "$BUDGET" ] || over_budget="yes"
  echo "Memory: $size_before -> $size_after tokens (budget $BUDGET)"

  # 4b. Judge the diff with memory-reviewer (AI-17). The script hands it the diff,
  #     and it only gets read-only tools, so the judge itself can't change anything.
  mkdir -p "$STATE_DIR/reviews"
  review_file="$STATE_DIR/reviews/$TODAY-$(git rev-parse --short HEAD).txt"
  { echo "Files changed on this branch compared with $BASE:"
    git diff --stat "$BASE...$BRANCH"
    echo; echo "Diff of memory/:"
    git diff "$BASE...$BRANCH" -- memory/
  } | pi -p --no-session --tools read,grep,find,ls @.pi/agents/memory-reviewer.md \
      "You are memory-reviewer. The dreaming branch $BRANCH is checked out. Its diff is above; you can't run commands, so judge from the diff and by reading files. Reply in the exact SCORE format from your instructions." \
      > "$review_file" || true

  # Pull the four numbers out of the "SCORE: n | accuracy n | deduplication n | scope n" line.
  score_line="$(grep -m1 -E '^SCORE: [1-5]' "$review_file" || true)"
  num() { printf '%s' "$score_line" | grep -oE "$1 [1-5]" | grep -oE '[1-5]$' || echo "-"; }
  score="$(num 'SCORE:')"; acc="$(num accuracy)"; dedup="$(num deduplication)"; scope="$(num scope)"

  # 4c. Merge into the base branch only if the judge's score reaches the threshold.
  #     No score (the judge failed or answered in the wrong format) never merges.
  merged="no"
  if [ "$over_budget" = "no" ] && [ "$score" != "-" ] && [ "$score" -ge "$MERGE_AT" ]; then
    git switch -q "$BASE"
    if git merge -q --no-edit "$BRANCH"; then
      merged="yes"
    else
      git merge --abort || true
      merged="conflict"
    fi
    git switch -q "$BRANCH"
  fi

  # One line per judged pass. Fill the "manual" column with your own 1-5 score
  # later, to check how far the judge agrees with you.
  [ -f "$JUDGE_LOG" ] || printf 'date\tbranch\tcommit\tscore\taccuracy\tdeduplication\tscope\tmerged\tmanual\n' > "$JUDGE_LOG"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\n' "$TODAY" "$BRANCH" "$(git rev-parse --short HEAD)" \
    "$score" "$acc" "$dedup" "$scope" "$merged" >> "$JUDGE_LOG"

  echo "Judge: score $score (accuracy $acc, deduplication $dedup, scope $scope); merged: $merged"
  case "$merged" in
    yes)      verdict=":white_check_mark: merged into \`$BASE\`" ;;
    conflict) verdict=":warning: score passed but the merge conflicted; left on \`$BRANCH\`" ;;
    *)        verdict=":eyes: below $MERGE_AT (or no score); left on \`$BRANCH\` for review" ;;
  esac
  [ "$over_budget" = "no" ] || verdict=":warning: memory is over budget ($size_after > $BUDGET tokens); left on \`$BRANCH\` for review"
  slack ":crescent_moon: Dreaming $TODAY: ${#new[@]} session(s), committed on \`$BRANCH\`.
Judge: *$score*/5 (accuracy $acc, dedup $dedup, scope $scope). Memory: $size_before -> $size_after tokens (budget $BUDGET). $verdict
\`\`\`$stat\`\`\`"
else
  echo "Dreaming made no memory changes."
  slack ":crescent_moon: Dreaming $TODAY: ${#new[@]} session(s), no memory changes."
fi

# 5. Mark these sessions done only after a successful run.
printf '%s\n' "${new[@]}" >> "$PROCESSED"
git switch -q "$START_BRANCH"
