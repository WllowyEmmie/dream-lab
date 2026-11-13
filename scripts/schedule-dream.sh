#!/usr/bin/env bash
# Schedules dream.sh to run nightly with cron (macOS and Linux).
#   scripts/schedule-dream.sh            # 02:00 nightly
#   scripts/schedule-dream.sh 23 30      # 23:30 nightly
#   scripts/schedule-dream.sh --remove
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
tag="# dream-lab:$repo"                      # marks this repo's line in the crontab

current="$(crontab -l 2>/dev/null | grep -vF "$tag" || true)"

if [ "${1:-}" = "--remove" ]; then
  printf '%s\n' "$current" | crontab -
  echo "Removed the dream-lab job for $repo."
  exit 0
fi

hour="${1:-2}"; minute="${2:-0}"
# cron starts with a near-empty PATH, so save the current one; that's how it finds pi.
line="$minute $hour * * * PATH='$PATH' cd '$repo' && mkdir -p .dream-state && ./dream.sh >> .dream-state/dream.log 2>&1 $tag"

printf '%s\n%s\n' "$current" "$line" | sed '/^$/d' | crontab -
echo "Scheduled dream.sh daily at $(printf '%02d:%02d' "$hour" "$minute")."
echo "Log: $repo/.dream-state/dream.log"
