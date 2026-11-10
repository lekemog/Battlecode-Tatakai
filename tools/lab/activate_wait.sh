#!/bin/bash
# activate_wait.sh N : make submission N live and WAIT until it really is (activation takes ~10 minutes; the old version stays live meanwhile).
N=${1:?usage: activate_wait.sh N}
for i in $(seq 1 20); do cambc submissions activate "$N" >/dev/null 2>&1 && break; sleep 20; done
for i in $(seq 1 120); do
  l=$(cambc submissions list --json 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin); rows=d if isinstance(d,list) else d.get('submissions',d)
print(' '.join(str(r['version']) for r in rows if r['active']))" 2>/dev/null)
  [ "$l" = "$N" ] && { echo "live: $N at $(date -u +%H:%M)"; exit 0; }; sleep 15
done
echo "version $N did not become live in 30 minutes"; exit 1
