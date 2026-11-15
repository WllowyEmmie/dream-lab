#!/usr/bin/env bash
# Eval suite (AI-23): runs the eval tasks under three memory setups and writes
# results.json.
#
#   none      no memory/ folder, and a harness with every memory rule removed
#   memory    memory as Pi left it after the learning tasks (notes never sorted)
#   dreaming  the same memory after one dreaming pass
#
# Pi does the learning tasks (01-06) once, in one workspace; "memory" and
# "dreaming" both start from those same notes, so dreaming is the only difference.
# Every eval run then gets its own fresh workspace holding just one task.
#
#   scripts/run-evals.sh                         everything: 3 setups x 15 tasks x 3 repeats
#   scripts/run-evals.sh --setup none            one setup (none | memory | dreaming)
#   scripts/run-evals.sh --group similar         one task group (similar | new | different)
#   scripts/run-evals.sh --task 07-member-shipping-discount --repeats 1
#
# Safe to stop and rerun: finished runs are skipped. To start over, delete the
# work folder (printed at the start) and .dream-state/evals/.
# Run from Git Bash. Commit your changes first: workspaces are built from HEAD.
set -euo pipefail

cd "$(dirname "$0")/.."
REPO="$(pwd)"
WORK="${EVAL_WORK:-$(dirname "$REPO")/dream-lab-evals}"   # outside the repo, so Pi can't see its AGENTS.md
RUNS="$REPO/.dream-state/evals/runs.jsonl"
RESULTS="$REPO/results.json"
STATE="$WORK/state"
LEARN="$WORK/learn"
TIMEOUT="${EVAL_TIMEOUT:-1500}"          # seconds per Pi run
# --approve: a new workspace isn't a trusted Pi project yet, and without trust
# Pi skips its .pi/skills.
PI_FLAGS="${EVAL_PI_FLAGS:---approve}"

SETUPS="none memory dreaming"; GROUP="all"; REPEATS=3; ONLY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --setup)   SETUPS="$2"; shift 2 ;;
    --group)   GROUP="$2"; shift 2 ;;
    --repeats) REPEATS="$2"; shift 2 ;;
    --task)    ONLY="$2"; shift 2 ;;
    *) sed -n '2,20p' "$0"; exit 2 ;;
  esac
done

PY=""
for c in python3 python py; do
  if "$c" -c "import unittest" > /dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "Python not found." >&2; exit 1; }
winpath() { cygpath -m "$1" 2>/dev/null || printf '%s' "$1"; }   # a path Pi on Windows can read
gitq() { git -c user.name="dream-lab eval" -c user.email="eval@dream-lab.invalid" "$@"; }
mkdir -p "$STATE" "$(dirname "$RUNS")"
echo "Work folder: $WORK"

# Run Pi in a folder. Sets PI_STATUS: 0 = finished, 124 = timed out.
# Any other failure (login expired, usage limit...) isn't a result: stop.
run_pi() {  # <folder> <session dir> <output file> <prompt>
  local dir="$1" sess="$2" out="$3" prompt="$4" limit=()
  command -v timeout > /dev/null && limit=(timeout "$TIMEOUT")
  mkdir -p "$sess"
  PI_STATUS=0
  # < /dev/null: Pi adds anything on stdin to its prompt, and this runs inside
  # loops that read the task list from stdin.
  ( cd "$dir" && ${limit[@]+"${limit[@]}"} pi -p $PI_FLAGS --session-dir "$(winpath "$sess")" "$prompt" ) \
    < /dev/null > "$out" 2> "$out.err" || PI_STATUS=$?
  if [ "$PI_STATUS" -ne 0 ] && [ "$PI_STATUS" -ne 124 ]; then
    echo "Pi failed to run, so the eval stopped. Fix it and rerun; finished runs are kept." >&2
    cat "$out.err" >&2
    exit 1
  fi
}

# Run one task with Pi in a folder that already holds it, then check and record.
do_task() {  # <setup> <group> <task> <repeat> <folder>
  local setup="$1" group="$2" id="$3" rep="$4" dir="$5"
  local sess="$WORK/sessions/$setup/$id-r$rep" before started
  rm -rf "$sess"
  before="$(cksum < "$dir/tasks/$id/test_task.py")"
  started=$SECONDS
  run_pi "$dir" "$sess" "$WORK/sessions/$setup/$id-r$rep.txt" \
    "Fix the bug described in tasks/$id/TASK.md. Follow AGENTS.md."
  local passed="no" edited="no" timed="no"
  [ "$PI_STATUS" -eq 124 ] && timed="yes"
  [ "$(cksum < "$dir/tasks/$id/test_task.py")" = "$before" ] || edited="yes"
  if [ "$edited" = "no" ] && ( cd "$dir/tasks/$id" && PYTHONDONTWRITEBYTECODE=1 "$PY" -m unittest -q ) > /dev/null 2>&1; then
    passed="yes"
  fi
  RUN_SETUP="$setup" RUN_GROUP="$group" RUN_TASK="$id" RUN_REPEAT="$rep" RUN_PASSED="$passed" \
    RUN_TEST_EDITED="$edited" RUN_TIMED_OUT="$timed" RUN_SECONDS="$((SECONDS - started))" RUN_SESSIONS="$sess" \
    RUN_USAGE="$(node scripts/usage.mjs --json --out none "$sess")" \
    node scripts/eval-results.mjs record "$RUNS"
}

needs_memory="no"
case " $SETUPS " in *" memory "*|*" dreaming "*) needs_memory="yes" ;; esac

# ---- Learning: Pi does tasks 01-06 in one workspace, building up memory. ----
if [ "$needs_memory" = "yes" ] && [ ! -f "$STATE/learned" ]; then
  if [ ! -d "$LEARN/.git" ]; then
    git clone -q "$REPO" "$LEARN"
    ( cd "$LEARN" && git config user.name "dream-lab eval" && git config user.email "eval@dream-lab.invalid" \
        && git rm -rq tasks && git commit -qm "Start with no tasks" )
  fi
  touch "$STATE/learned.txt"
  while read -r id group; do
    grep -qxF "$id" "$STATE/learned.txt" && continue
    echo "== learning: $id"
    git archive HEAD "tasks/$id" | tar -x -C "$LEARN"
    ( cd "$LEARN" && git add -A && gitq commit -qm "Add task $id" )
    do_task learning learn "$id" 1 "$LEARN"
    ( cd "$LEARN" && git add -A && gitq commit -qm "After task $id" --allow-empty )
    echo "$id" >> "$STATE/learned.txt"
  done < <(node scripts/eval-results.mjs tasks learn)
  mkdir -p "$STATE/memory/memory"
  cp "$LEARN"/memory/*.md "$STATE/memory/memory/"
  touch "$STATE/learned"
fi

# ---- Dreaming: one real dream.sh pass over the learning sessions. ----
case " $SETUPS " in *" dreaming "*)
  if [ ! -f "$STATE/dreamed" ]; then
    echo "== dreaming pass over the learning sessions"
    ( cd "$LEARN"
      PI_CODING_AGENT_SESSION_DIR="$WORK/sessions/learning" DREAM_BRANCH="dreaming/eval" \
        DREAM_BASE="$(git branch --show-current)" DREAM_PI_FLAGS="$PI_FLAGS" ./dream.sh < /dev/null
      if ! git show-ref --verify --quiet refs/heads/dreaming/eval; then
        echo "dream.sh found no learning sessions to dream over. Stopping." >&2; exit 1
      fi
      if [ -n "$(git status --porcelain)" ]; then
        echo "The dreaming pass left uncommitted changes in $LEARN. Stopping." >&2; exit 1
      fi
      # The eval measures dreaming itself, so its memory is used whatever the
      # judge decided; the judge's score is saved with the results.
      gitq merge -q --no-edit dreaming/eval
      node -e '
        const fs = require("fs");
        const last = (f) => { try { const l = fs.readFileSync(f, "utf8").trim().split("\n"); return l.length > 1 ? l.pop().split("\t") : null; } catch { return null; } };
        const j = last(".dream-state/judge-log.tsv"), m = last(".dream-state/memory-size.tsv");
        const u = { tokens: 0, cost_usd: 0 };
        try { for (const l of fs.readFileSync(".dream-state/usage.csv", "utf8").trim().split("\n").slice(1)) {
          const c = l.split(","); if (c[1] === "dream" || c[1] === "judge") { u.tokens += Number(c[9]); u.cost_usd += Number(c[10]); } } } catch {}
        fs.writeFileSync(process.argv[1], JSON.stringify({
          judge_score: j ? Number(j[3]) || null : null, auto_merged: j ? j[7] : null,
          memory_tokens_before: m ? Number(m[2]) : null, memory_tokens_after: m ? Number(m[3]) : null,
          tokens: u.tokens, cost_usd: Number(u.cost_usd.toFixed(6)) }, null, 2));
      ' "$(winpath "$STATE/dream.json")"
    )
    mkdir -p "$STATE/dreaming/memory"
    cp "$LEARN"/memory/*.md "$STATE/dreaming/memory/"
    touch "$STATE/dreamed"
  fi ;;
esac

# ---- Eval runs: a fresh workspace per run, holding only that task. ----
for setup in $SETUPS; do
  case "$setup" in none|memory|dreaming) ;; *) echo "Unknown setup: $setup" >&2; exit 2 ;; esac
  while read -r id group; do
    [ "$group" = "learn" ] && continue
    [ -z "$ONLY" ] || [ "$ONLY" = "$id" ] || continue
    for rep in $(seq "$REPEATS"); do
      node scripts/eval-results.mjs has "$RUNS" "$setup" "$id" "$rep" && continue
      echo "== $setup / $id / run $rep"
      ws="$WORK/runs/$setup/$id-r$rep"
      rm -rf "$ws"; mkdir -p "$ws"
      git archive HEAD AGENTS.md .pi .gitignore "tasks/$id" | tar -x -C "$ws"
      if [ "$setup" = "none" ]; then
        git archive HEAD:evals/no-memory | tar -x -C "$ws"
        rm -rf "$ws/.pi/skills/record-mistake" "$ws/.pi/agents/memory-reviewer.md"
      else
        mkdir -p "$ws/memory"
        cp "$STATE/$setup/memory"/*.md "$ws/memory/"
      fi
      ( cd "$ws" && git init -q && git add -A && gitq commit -qm "Start of run" )
      do_task "$setup" "$group" "$id" "$rep" "$ws"
    done
  done < <(node scripts/eval-results.mjs tasks "$GROUP")
done

echo
node scripts/eval-results.mjs summarize "$RUNS" "$RESULTS" "$STATE"
echo "Results: results.json   Every run: .dream-state/evals/runs.jsonl"
