#!/bin/bash
# live_status.sh : prints the live (active) submission version, the newest 5 versions with status, and whether the CLI is signed in.
cambc submissions list --json 2>&1 | python3 -c "
import json,sys
raw=sys.stdin.read()
try: d=json.loads(raw)
except Exception: print('NOT SIGNED IN or rate limited:', raw[:150]); sys.exit(1)
rows=d if isinstance(d,list) else d.get('submissions',d)
print('LIVE:', [r['version'] for r in rows if r['active']])
for r in rows[:5]: print(' ', r['version'], r['status'], r['createdAt'][:16], r['fileName'])"
