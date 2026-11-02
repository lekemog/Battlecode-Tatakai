#!/bin/bash
# panel_run.sh PANEL_FILE LABEL VERSION [BASE_LABEL] : run the pinned real-opponent panel for submission VERSION (it must already exist).
# Safe wrapper: checks you are signed in, prints the live version before/after, runs at most 4 attempts (each failed attempt can create a
# new match group and burn unranked quota), and does NOT change the live version afterwards (the panel makes VERSION live and waits for it).
# Run it from the repo root. Examples:
#   tools/lab/panel_run.sh tools/panel/panel_strong.json   base 226                # baseline: opponents' current bots
#   tools/lab/panel_run.sh tools/panel/panel_strong.json   cand 227 base           # candidate, opponents pinned to the baseline run
P=${1:?usage: panel_run.sh PANEL_FILE LABEL VERSION [BASE_LABEL]}; L=${2:?}; V=${3:?}; BASE=$4
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
tools/lab/live_status.sh || exit 1
export PANEL_FILE=$P
for i in 1 2 3 4; do
  if [ -n "$BASE" ]; then python3 -I tools/panel/panel.py run "$L" "$V" --pin "$BASE" && break
  else python3 -I tools/panel/panel.py run "$L" "$V" && break; fi
  echo "attempt $i failed at $(date -u +%H:%M:%S); waiting 45 s"; sleep 45
done
tools/lab/live_status.sh
[ -n "$BASE" ] && python3 -I tools/panel/panel.py compare "$BASE" "$L" | tail -6
echo "Panel done. The live version is whatever it printed above: restore the intended bot with tools/lab/activate_wait.sh N."
