#!/bin/bash
# stallscan.sh BOT OPP -> per map: final gems, idle turn count, bank turns, longest same-tile streak of a living champion
B=$1;O=$2;OUT=/home/claude/data/stallscan/$B-$O.txt;: > $OUT
for m in $(tr ',' ' ' < /home/claude/tools/pool3.txt); do
  D=$(timeout 900 python3 -I /home/claude/tools/quickgame.py $B $O $m 2>&1 | grep '^dir' | awk '{print $2}')
  [ -z "$D" ] && { echo "$m FAIL" >> $OUT; continue; }
  python3 -I - "$D" "$m" >> $OUT <<'P'
import json,sys,subprocess
D,m=sys.argv[1],sys.argv[2]
R=json.load(open(D+'/r.json'))['rounds'];T=len(R)-1
log=subprocess.run(['strings',D+'/team-a.stdout'],capture_output=True,text=True).stdout.split('\n')
acts=[l.split()[3] for l in log if l.startswith('T ') and len(l.split())>3]
idle=acts.count('idle');bank=acts.count('bank')
best=0;last={};run={}
for t in range(1,T+1):
  for c in R[t]['champions']:
    if c['team']!=0 or not c.get('alive') or not c.get('position'):continue
    k=c['entity']['index'];p=(c['position']['x'],c['position']['y'])
    run[k]=run.get(k,0)+1 if last.get(k)==p else 0;last[k]=p;best=max(best,run[k])
print(f"{m:24} gems {R[T]['submittedGems'][0]:5}-{R[T]['submittedGems'][1]:5} idle {idle:5} bank {bank:4} still {best}")
P
  rm -rf "$D"
done
