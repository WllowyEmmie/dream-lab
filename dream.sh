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

mkdir -p "$STATE_DIR"; touch "$PROCESSED"

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
pi -p --no-session @prompts/dream.md "TODAY: $TODAY

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
  slack ":crescent_moon: Dreaming $TODAY: ${#new[@]} session(s), committed on \`$BRANCH\`.
\`\`\`$(git show --stat --format= HEAD)\`\`\`"
else
  echo "Dreaming made no memory changes."
  slack ":crescent_moon: Dreaming $TODAY: ${#new[@]} session(s), no memory changes."
fi

# 5. Mark these sessions done only after a successful run.
printf '%s\n' "${new[@]}" >> "$PROCESSED"
git switch -q "$START_BRANCH"
