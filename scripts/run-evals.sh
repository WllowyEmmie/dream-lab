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
#   scripts/run-evals.sh --suite hard            the harder task set (tasks-hard/), scored with hidden tests
#   scripts/run-evals.sh --setup none            one setup (none | memory | dreaming)
#   scripts/run-evals.sh --group similar         one task group (similar | new | different)
#   scripts/run-evals.sh --task 07-member-shipping-discount --repeats 1
#   scripts/run-evals.sh --suite hard --rounds 6 the rounds experiment: every setup does all the tasks, round
#                                                after round; memory carries over, and the dreaming setup
#                                                dreams between rounds
#   scripts/run-evals.sh ... --max-runs 3        stop after 3 runs; run the same command again to continue
#   scripts/run-evals.sh ... --model claude-haiku-5-5
#                                                run every Pi call (tasks, dreaming, judge) on that model;
#                                                its work folder and results are kept apart from the default
#                                                model's (provider claude-bridge unless --provider says)
#   scripts/run-evals.sh ... --label harness-v2  keep this run's work folder and results apart under a name,
#                                                e.g. after changing the harness; combines with --model
#   scripts/run-evals.sh --manual ...            you run Pi yourself in T3 Code: for each run the script
#                                                builds the folder, shows the prompt and waits for you
#
# Safe to stop and rerun: finished runs are skipped. To start over, delete the
# work folder (printed at the start) and the runs file in .dream-state/evals/.
# Run from Git Bash. Commit your changes first: workspaces are built from HEAD.
set -euo pipefail

cd "$(dirname "$0")/.."
REPO="$(pwd)"
TIMEOUT="${EVAL_TIMEOUT:-1500}"          # seconds per Pi run
# --approve: a new workspace isn't a trusted Pi project yet, and without trust
# Pi skips its .pi/skills.
PI_FLAGS="${EVAL_PI_FLAGS:---approve}"

SETUPS="none memory dreaming"; GROUP="all"; REPEATS=3; ONLY=""; SUITE="easy"; MANUAL="no"; ROUNDS=""; MAX_RUNS=""; RUN_COUNT=0; MODEL=""; PROVIDER=""; LABEL=""
while [ $# -gt 0 ]; do
  case "$1" in
    --suite)   SUITE="$2"; shift 2 ;;
    --manual)  MANUAL="yes"; shift ;;
    --rounds)  ROUNDS="$2"; shift 2 ;;
    --max-runs) MAX_RUNS="$2"; shift 2 ;;
    --setup)   SETUPS="$2"; shift 2 ;;
    --group)   GROUP="$2"; shift 2 ;;
    --repeats) REPEATS="$2"; shift 2 ;;
    --task)    ONLY="$2"; shift 2 ;;
    --model)    MODEL="$2"; shift 2 ;;
    --provider) PROVIDER="$2"; shift 2 ;;
    --label)    LABEL="$2"; shift 2 ;;
    *) sed -n '2,33p' "$0"; exit 2 ;;
  esac
done

# Each suite has its own tasks, work folder and results, so they never mix.
WORK="${EVAL_WORK:-$(dirname "$REPO")/dream-lab-evals}"   # outside the repo, so Pi can't see its AGENTS.md
case "$SUITE" in
  easy) TASKS_SRC="tasks"; HIDDEN_SRC=""; ASK="Fix the bug described in"
        RUNS="$REPO/.dream-state/evals/runs.jsonl"; RESULTS="$REPO/results.json" ;;
  hard) TASKS_SRC="tasks-hard"; HIDDEN_SRC="evals/hidden/hard"; ASK="Do the task described in"
        WORK="$WORK/hard"
        RUNS="$REPO/.dream-state/evals/runs-hard.jsonl"; RESULTS="$REPO/results-hard.json" ;;
  veryhard) TASKS_SRC="tasks-veryhard"; HIDDEN_SRC="evals/hidden/veryhard"; ASK="Do the task described in"
        WORK="$WORK/veryhard"
        RUNS="$REPO/.dream-state/evals/runs-veryhard.jsonl"; RESULTS="$REPO/results-veryhard.json" ;;
  *) echo "Unknown suite: $SUITE (easy, hard or veryhard)" >&2; exit 2 ;;
esac
if [ -n "$ROUNDS" ]; then      # the rounds experiment keeps its own folder and results
  WORK="${EVAL_WORK:-$(dirname "$REPO")/dream-lab-evals}/rounds/$SUITE"
  RUNS="$REPO/.dream-state/evals/rounds-$SUITE.jsonl"
fi
# --model / --label: the run gets its own work folder (so its own memory) and results,
# under models/<model>[-<label>] ("default" when only a label is given).
if [ -n "$MODEL" ] || [ -n "$LABEL" ]; then
  case "$MODEL$LABEL" in *[!A-Za-z0-9._-]*) echo "Model and label may use only letters, digits, . _ -" >&2; exit 2 ;; esac
  if [ -n "$MODEL" ]; then
    PROVIDER="${PROVIDER:-claude-bridge}"
    PI_FLAGS="$PI_FLAGS --provider $PROVIDER --model $MODEL"
    echo "Model: $MODEL (provider $PROVIDER)"
  fi
  TAG="${MODEL:-default}${LABEL:+-$LABEL}"
  [ -z "$LABEL" ] || echo "Label: $LABEL"
  base="${EVAL_WORK:-$(dirname "$REPO")/dream-lab-evals}"
  WORK="$base/models/$TAG${WORK#$base}"
  RUNS="$(dirname "$RUNS")/models/$TAG/$(basename "$RUNS")"
  RESULTS="${RESULTS%.json}-$TAG.json"
fi
STATE="$WORK/state"
LEARN="$WORK/learn"
# --max-runs: stop between runs, once this call has done that many.
maybe_stop() {
  RUN_COUNT=$((RUN_COUNT + 1))
  if [ -n "$MAX_RUNS" ] && [ "$RUN_COUNT" -ge "$MAX_RUNS" ]; then
    echo; echo "MORE: stopped after $RUN_COUNT runs. Run the same command again to continue."
    exit 0
  fi
}
# Workspaces get the repo's Pi setup, minus the skill for running these evals.
get_harness() { git archive HEAD "$@" | tar -x -C "$DEST" && rm -rf "$DEST/.pi/skills/run-evals"; }
list_tasks() { node scripts/eval-results.mjs tasks "$1" "$TASKS_SRC/tasks.json"; }
# Put one task into a workspace as tasks/<id>, straight from the last commit.
add_task() { mkdir -p "$2/tasks/$1" && git archive "HEAD:$TASKS_SRC/$1" | tar -x -C "$2/tasks/$1"; }

PY=""
for c in python3 python py; do
  if "$c" -c "import unittest" > /dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "Python not found." >&2; exit 1; }
winpath() { cygpath -m "$1" 2>/dev/null || printf '%s' "$1"; }   # a path Pi on Windows can read
gitq() { git -c user.name="dream-lab eval" -c user.email="eval@dream-lab.invalid" "$@"; }
mkdir -p "$STATE" "$(dirname "$RUNS")"
echo "Work folder: $WORK"

# ---- Slack: posts after each round, when a run stops early, and when all is done ----
# Uses SLACK_WEBHOOK_URL from the repo's .env, like dream.sh. Without it, nothing is
# posted. EVAL_SLACK=0 turns it off for one run. A failed post never stops the eval.
if [ -z "${SLACK_WEBHOOK_URL:-}" ] && [ -f "$REPO/.env" ]; then
  SLACK_WEBHOOK_URL="$(tr -d '\r' < "$REPO/.env" | sed -n 's/^SLACK_WEBHOOK_URL=//p' | tail -n 1)"
fi
[ "${EVAL_SLACK:-1}" = "0" ] && SLACK_WEBHOOK_URL=""
slack() {
  [ -n "${SLACK_WEBHOOK_URL:-}" ] || return 0
  local payload
  payload="$(node -e 'process.stdout.write(JSON.stringify({text: process.argv[1]}))' "$1")" || return 0
  curl -fsS -m 20 -X POST -H 'Content-Type: application/json' --data "$payload" "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 \
    || echo "(Slack post failed; the eval carries on.)" >&2
}
SUITE_NAME="$SUITE"; [ "$SUITE" = "veryhard" ] && SUITE_NAME="very hard"
[ -z "$MODEL" ] || SUITE_NAME="$SUITE_NAME, $MODEL"
[ -z "$LABEL" ] || SUITE_NAME="$SUITE_NAME, $LABEL"

# --manual: you run Pi in T3 Code. Show what to open and paste, wait, then copy
# the sessions Pi saved for that folder so turns and tokens can still be counted.
norm() { printf '%s' "$1" | sed 's#\\\\#/#g; s#\\#/#g; s#/*$##' | tr '[:upper:]' '[:lower:]'; }
manual_run() {  # <folder> <session dir> <prompt>
  local dir="$1" sess="$2" prompt="$3" root="${PI_CODING_AGENT_SESSION_DIR:-$HOME/.pi/agent/sessions}" want f cwd n=0
  touch "$sess/.start"
  echo
  echo "  1. In T3 Code, open this folder as a project:"
  echo "       $(winpath "$dir")"
  echo "  2. Start a new chat with Pi and send:"
  echo "       $prompt"
  echo "  3. When Pi has finished, come back here."
  if [ -n "${EVAL_MANUAL_HOOK:-}" ]; then "$EVAL_MANUAL_HOOK" "$dir" "$prompt" < /dev/null      # used by tests
  else read -r -p "  Press Enter when Pi has finished... " _ < /dev/tty || true; fi
  want="$(norm "$(cd "$dir" && { pwd -W 2> /dev/null || pwd; })")"
  while IFS= read -r -d '' f; do
    cwd="$(head -n 1 "$f" | grep -o '"cwd":"[^"]*"' | sed 's/^"cwd":"//; s/"$//' || true)"
    [ "$(norm "$cwd")" = "$want" ] || continue
    cp "$f" "$sess/"; n=$((n + 1))
  done < <(find "$root" -name '*.jsonl' -newer "$sess/.start" -print0 2> /dev/null)
  [ "$n" -gt 0 ] || echo "  (No Pi session file found for this folder, so turns and tokens are recorded as 0. Pass or fail is still checked.)"
}

# Run Pi in a folder. Sets PI_STATUS: 0 = finished, 124 = timed out.
# Any other failure (login expired, usage limit...) isn't a result: stop.
run_pi() {  # <folder> <session dir> <output file> <prompt>
  local dir="$1" sess="$2" out="$3" prompt="$4" limit=()
  command -v timeout > /dev/null && limit=(timeout "$TIMEOUT")
  mkdir -p "$sess"
  PI_STATUS=0
  if [ "$MANUAL" = "yes" ]; then manual_run "$dir" "$sess" "$prompt"; return; fi
  # < /dev/null: Pi adds anything on stdin to its prompt, and this runs inside
  # loops that read the task list from stdin.
  ( cd "$dir" && ${limit[@]+"${limit[@]}"} pi -p $PI_FLAGS --session-dir "$(winpath "$sess")" "$prompt" ) \
    < /dev/null > "$out" 2> "$out.err" || PI_STATUS=$?
  if [ "$PI_STATUS" -ne 0 ] && [ "$PI_STATUS" -ne 124 ]; then
    echo "Pi failed to run, so the eval stopped. Fix it and rerun; finished runs are kept." >&2
    cat "$out.err" >&2
    local why
    why="$( { tail -n 3 "$out.err"; tail -n 3 "$out"; } 2> /dev/null | grep -v '^[[:space:]]*$' | tail -n 3 )"
    slack ":octagonal_sign: dream-lab eval ($SUITE_NAME tasks) stopped: Pi couldn't run. Finished runs are kept; run the same command again to continue.
\`\`\`${why:-no error text}\`\`\`"
    exit 1
  fi
}

# Run one task with Pi in a folder that already holds it, then check and record.
do_task() {  # <setup> <group> <task> <repeat> <folder>
  local setup="$1" group="$2" id="$3" rep="$4" dir="$5"
  local sess="${SESS_BASE:-$WORK/sessions/$setup}/$id-r$rep" before started
  rm -rf "$sess"
  before="$(cksum < "$dir/tasks/$id/test_task.py")"
  started=$SECONDS
  run_pi "$dir" "$sess" "$sess.txt" \
    "$ASK tasks/$id/TASK.md. Follow AGENTS.md."
  [ -z "${AFTER_PI:-}" ] || "$AFTER_PI" "$dir" "$id"     # before the hidden test is copied in
  local seconds=$((SECONDS - started)) visible="no" passed="no" edited="no" timed="no" hidden="0 0" tlimit=()
  command -v timeout > /dev/null && tlimit=(timeout 120)     # in case the code under test never returns
  [ "$PI_STATUS" -eq 124 ] && timed="yes"
  [ "$(cksum < "$dir/tasks/$id/test_task.py")" = "$before" ] || edited="yes"
  if ( cd "$dir/tasks/$id" && PYTHONDONTWRITEBYTECODE=1 ${tlimit[@]+"${tlimit[@]}"} "$PY" -m unittest -q test_task ) > /dev/null 2>&1; then
    visible="yes"
  fi
  # The hidden test is only copied in now, after Pi has finished.
  if [ -n "$HIDDEN_SRC" ] && git cat-file -e "HEAD:$HIDDEN_SRC/$id/test_hidden.py" 2> /dev/null; then
    git show "HEAD:$HIDDEN_SRC/$id/test_hidden.py" > "$dir/tasks/$id/test_hidden.py"
    hidden="$( cd "$dir/tasks/$id" && PYTHONDONTWRITEBYTECODE=1 ${tlimit[@]+"${tlimit[@]}"} "$PY" "$REPO/scripts/count-tests.py" test_hidden 2> /dev/null )" || hidden="0 1"
    [ -n "$hidden" ] || hidden="0 1"
  fi
  # Passed = the visible test and every hidden test pass, and the test file is untouched.
  if [ "$visible" = "yes" ] && [ "$edited" = "no" ] && [ "${hidden% *}" = "${hidden#* }" ]; then passed="yes"; fi
  RUN_MODEL="${MODEL:-default}" RUN_LABEL="$LABEL" RUN_SETUP="$setup" RUN_GROUP="$group" RUN_TASK="$id" RUN_REPEAT="$rep" RUN_PASSED="$passed" RUN_VISIBLE="$visible" \
    RUN_HIDDEN_PASSED="${hidden% *}" RUN_HIDDEN_TOTAL="${hidden#* }" \
    RUN_TEST_EDITED="$edited" RUN_TIMED_OUT="$timed" RUN_SECONDS="$seconds" RUN_SESSIONS="$sess" \
    RUN_USAGE="$(node scripts/usage.mjs --json --out none "$sess")" \
    node scripts/eval-results.mjs record "$RUNS"
}

# ---- Rounds: every setup does all the tasks, round after round. ----
# Each task still gets a fresh workspace. In the memory setups it starts with the
# notes every earlier task left, kept in a "home" repo per setup, together with the
# code as Pi last left it (so dreaming has code to check notes against).
# The dreaming setup runs one dreaming pass over a round's sessions before the next round.
if [ -n "$ROUNDS" ]; then
  EXTRA="${RUNS%.jsonl}-extra.jsonl"     # memory size and dreaming passes, per round
  extra() { node -e 'require("fs").appendFileSync(process.argv[1], process.argv[2] + "\n")' "$(winpath "$EXTRA")" "$1"; }
  mem_tokens() { cat "$1"/memory/*.md 2> /dev/null | wc -m | awk '{print int(($1 + 3) / 4)}'; }
  keep_work() {  # <workspace> <task>: carry the notes and the task's code back to the setup's home
    [ -n "$CUR_HOME" ] || return 0
    [ ! -f "$1/memory/inbox.md" ] || cp "$1/memory/inbox.md" "$CUR_HOME/memory/inbox.md"
    rm -rf "$CUR_HOME/tasks/$2"; mkdir -p "$CUR_HOME/tasks"
    cp -r "$1/tasks/$2" "$CUR_HOME/tasks/$2"
    find "$CUR_HOME/tasks/$2" -name __pycache__ -type d -prune -exec rm -rf {} +
    ( cd "$CUR_HOME" && git add -A && git commit -qm "After $2" --allow-empty )
  }
  AFTER_PI=keep_work
  for setup in $SETUPS; do
    case "$setup" in none|memory|dreaming) ;; *) echo "Unknown setup: $setup" >&2; exit 2 ;; esac
    CUR_HOME=""
    if [ "$setup" != "none" ]; then
      CUR_HOME="$WORK/$setup/home"
      if [ ! -d "$CUR_HOME/.git" ]; then
        mkdir -p "$CUR_HOME"
        DEST="$CUR_HOME" get_harness AGENTS.md .pi .gitignore memory dream.sh prompts scripts
        ( cd "$CUR_HOME" && git init -q && git config user.name "dream-lab eval" && git config user.email "eval@dream-lab.invalid" \
            && git add -A && git commit -qm "Start" )
      fi
    fi
    for round in $(seq "$ROUNDS"); do
      SESS_BASE="$WORK/sessions/$setup/round-$round"
      while read -r id group; do
        [ -z "$ONLY" ] || [ "$ONLY" = "$id" ] || continue
        node scripts/eval-results.mjs has "$RUNS" "$setup" "$id" "$round" && continue
        echo "== $setup / round $round / $id"
        ws="$WORK/$setup/runs/round-$round/$id"
        rm -rf "$ws"; mkdir -p "$ws"
        DEST="$ws" get_harness AGENTS.md .pi .gitignore
        add_task "$id" "$ws"
        if [ "$setup" = "none" ]; then
          git archive HEAD:evals/no-memory | tar -x -C "$ws"
          rm -rf "$ws/.pi/skills/record-mistake" "$ws/.pi/agents/memory-reviewer.md"
        else
          mkdir -p "$ws/memory"
          cp "$CUR_HOME"/memory/*.md "$ws/memory/"
        fi
        ( cd "$ws" && git init -q && git add -A && gitq commit -qm "Start of run" )
        do_task "$setup" "$group" "$id" "$round" "$ws"
        maybe_stop
      done < <(list_tasks all)
      # End of the round, once: note how big memory got, then dream if this setup dreams.
      [ -z "$ONLY" ] && [ ! -f "$WORK/$setup/round-$round.done" ] || continue
      mkdir -p "$WORK/$setup"
      [ "$setup" = "none" ] || extra "{\"kind\":\"memory\",\"setup\":\"$setup\",\"round\":$round,\"memory_tokens\":$(mem_tokens "$CUR_HOME")}"
      if [ "$setup" = "dreaming" ] && [ "$round" -lt "$ROUNDS" ]; then
        echo "== dreaming pass after round $round"
        started=$SECONDS
        ( cd "$CUR_HOME"
          lines=0; [ ! -f .dream-state/usage.csv ] || lines="$(wc -l < .dream-state/usage.csv)"
          # SLACK_WEBHOOK_URL="": the round's own Slack message reports this pass.
          SLACK_WEBHOOK_URL="" PI_CODING_AGENT_SESSION_DIR="$SESS_BASE" DREAM_ANY_CWD=1 DREAM_BRANCH="dreaming/round-$round" \
            DREAM_BASE="$(git branch --show-current)" DREAM_PI_FLAGS="$PI_FLAGS" ./dream.sh < /dev/null
          if [ -n "$(git status --porcelain)" ]; then
            echo "The dreaming pass left uncommitted changes in $CUR_HOME. Stopping." >&2; exit 1
          fi
          if ! git show-ref --verify --quiet "refs/heads/dreaming/round-$round"; then
            echo "dream.sh found no sessions from round $round to dream over. Stopping." >&2; exit 1
          fi
          gitq merge -q --no-edit "dreaming/round-$round"      # used whatever the judge scored; the score is saved
          node -e '
            const fs = require("fs");
            const last = (f) => { try { const l = fs.readFileSync(f, "utf8").trim().split("\n"); return l.length > 1 ? l.pop().split("\t") : null; } catch { return null; } };
            const j = last(".dream-state/judge-log.tsv"), m = last(".dream-state/memory-size.tsv");
            const [out, setup, round, seconds, skip] = process.argv.slice(1);
            let tokens = 0, cost = 0;
            try { for (const l of fs.readFileSync(".dream-state/usage.csv", "utf8").trim().split("\n").slice(Math.max(1, Number(skip)))) {
              const c = l.split(","); if (c[1] === "dream" || c[1] === "judge") { tokens += Number(c[9]); cost += Number(c[10]); } } } catch {}
            fs.appendFileSync(out, JSON.stringify({ kind: "dream", setup, round: Number(round), seconds: Number(seconds), tokens,
              cost_usd: Number(cost.toFixed(6)), judge_score: j ? Number(j[3]) || null : null,
              memory_before: m ? Number(m[2]) : null, memory_after: m ? Number(m[3]) : null }) + "\n");
          ' "$(winpath "$EXTRA")" "$setup" "$round" "$((SECONDS - started))" "$lines"
        )
      fi
      touch "$WORK/$setup/round-$round.done"
      slack "$(node scripts/eval-results.mjs line "$(winpath "$RUNS")" "$setup" "$round" "$(winpath "$EXTRA")" "$SUITE_NAME" "$ROUNDS")"
    done
  done
  echo
  echo "DONE: all runs finished."
  if [ -z "$ONLY" ] && [ ! -f "$WORK/summary-posted" ]; then
    complete="yes"
    for setup in none memory dreaming; do [ -f "$WORK/$setup/round-$ROUNDS.done" ] || complete="no"; done
    if [ "$complete" = "yes" ]; then
      slack "$(node scripts/eval-results.mjs line "$(winpath "$RUNS")" all 0 "$(winpath "$EXTRA")" "$SUITE_NAME" "$ROUNDS")"
      touch "$WORK/summary-posted"
    fi
  fi
  echo "Every run: ${RUNS#$REPO/}   Build the results page: node scripts/build-report.mjs"
  exit 0
fi

needs_memory="no"
case " $SETUPS " in *" memory "*|*" dreaming "*) needs_memory="yes" ;; esac

# ---- Learning: Pi does tasks 01-06 in one workspace, building up memory. ----
if [ "$needs_memory" = "yes" ] && [ ! -f "$STATE/learned" ]; then
  if [ ! -d "$LEARN/.git" ]; then
    # A new repo, not a clone: a clone's history would hold every task and hidden test.
    mkdir -p "$LEARN"
    DEST="$LEARN" get_harness AGENTS.md .pi .gitignore memory dream.sh prompts scripts
    ( cd "$LEARN" && git init -q && git config user.name "dream-lab eval" && git config user.email "eval@dream-lab.invalid" \
        && git add -A && git commit -qm "Start with no tasks" )
  fi
  touch "$STATE/learned.txt"
  while read -r id group; do
    grep -qxF "$id" "$STATE/learned.txt" && continue
    echo "== learning: $id"
    add_task "$id" "$LEARN"
    ( cd "$LEARN" && git add -A && gitq commit -qm "Add task $id" )
    do_task learning learn "$id" 1 "$LEARN"
    ( cd "$LEARN" && git add -A && gitq commit -qm "After task $id" --allow-empty )
    echo "$id" >> "$STATE/learned.txt"
    maybe_stop
  done < <(list_tasks learn)
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
      DEST="$ws" get_harness AGENTS.md .pi .gitignore
      add_task "$id" "$ws"
      if [ "$setup" = "none" ]; then
        git archive HEAD:evals/no-memory | tar -x -C "$ws"
        rm -rf "$ws/.pi/skills/record-mistake" "$ws/.pi/agents/memory-reviewer.md"
      else
        mkdir -p "$ws/memory"
        cp "$STATE/$setup/memory"/*.md "$ws/memory/"
      fi
      ( cd "$ws" && git init -q && git add -A && gitq commit -qm "Start of run" )
      do_task "$setup" "$group" "$id" "$rep" "$ws"
      maybe_stop
    done
  done < <(list_tasks "$GROUP")
done

echo
summary="$(node scripts/eval-results.mjs summarize "$RUNS" "$RESULTS" "$STATE")"
echo "$summary"
echo "DONE: all runs finished."
if [ -z "$ONLY" ] && [ "$GROUP" = "all" ]; then
  key="$(printf '%s' "$SETUPS $REPEATS" | tr ' ' '_')"
  if [ ! -f "$STATE/posted-$key" ]; then
    slack ":white_check_mark: dream-lab eval finished: $SUITE_NAME tasks, setups $SETUPS, $REPEATS run(s) each.
\`\`\`$summary\`\`\`"
    touch "$STATE/posted-$key"
  fi
fi
echo "Results: ${RESULTS#$REPO/}   Every run: ${RUNS#$REPO/}"
