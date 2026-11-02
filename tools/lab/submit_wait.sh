#!/bin/bash
# submit_wait.sh BOT_DIR : submit a bot folder and wait until its build is live. SUBMITTING REPLACES THE LIVE BOT (it activates automatically
# once built). Check LIVE_SLOT.md first and log the submission in SUBMISSIONS.md. Prints the new version number.
D=${1:?usage: submit_wait.sh BOT_DIR}
v=""; for i in $(seq 1 10); do out=$(cambc submit "$D" 2>&1 | tail -1); v=$(echo "$out" | grep -o 'version [0-9]*' | grep -o '[0-9]*'); [ -n "$v" ] && break; echo "$out" | cut -c1-120; sleep 30; done
[ -z "$v" ] && { echo "submit failed"; exit 1; }
echo "submitted version $v"
for i in $(seq 1 120); do
  l=$(cambc submissions list --json 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin); rows=d if isinstance(d,list) else d.get('submissions',d)
print(' '.join(str(r['version']) for r in rows if r['active']))" 2>/dev/null)
  [ "$l" = "$v" ] && { echo "live: $v at $(date -u +%H:%M)"; exit 0; }; sleep 15
done
echo "version $v not live after 30 minutes"; exit 1
