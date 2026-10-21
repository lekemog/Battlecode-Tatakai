#!/bin/bash
# waitgroups.sh GROUP... -> wait until all scrim groups are finished, then print results
while true; do
  done_all=1
  for g in "$@"; do
    s=$(cambc match-groups show $g --json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print(all(m.get('status') in ('finished','failed','error') for m in d['matches']))")
    [ "$s" != "True" ] && done_all=0
  done
  [ $done_all = 1 ] && break
  sleep 30
done
for g in "$@"; do cambc match-groups show $g --json 2>/dev/null | python3 -c "
import json,sys;d=json.load(sys.stdin)
op=[t.get('name') for t in d['matches'][0]['teams'] if not t.get('teamId','').startswith('9c16')][0]
print(op[:18].ljust(18),' '.join(m['map'][2:10]+':'+([t.get('result') or '?' for t in m['teams'] if t.get('teamId','').startswith('9c16')][0])[0] for m in d['matches']))"; done
