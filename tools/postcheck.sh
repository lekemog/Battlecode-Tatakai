#!/bin/bash
# postcheck.sh BOT OPP MAPFILE... : score, our deaths, share of trace lines in defensive posture
S=/tmp/claude-0/-home-claude/1a6e1a21-0974-5904-af74-73034a4d3e04/scratchpad/pc; mkdir -p $S
B=$1;O=$2;shift 2
for m in "$@"; do for side in A B; do
  if [ $side = A ]; then a=$B; b=$O; tf=team-a.stdout; else a=$O; b=$B; tf=team-b.stdout; fi
  out=$(cd /home/claude/proj && timeout 900 cambc run bots/$a bots/$b --map maps/$m.map26a --release 2>&1 | tail -3 | head -2 | awk '{print $3}' | tr '\n' '-')
  f=$(ls -t /home/claude/proj/replays/$a-vs-$b-*.repl26a | head -1); rm -rf $S/x; mkdir -p $S/x; (cd $S/x && unzip -o -q $f)
  df=$(tr -d '\000' < $S/x/$tf | grep -a "^T " | awk '{n++; if(substr($11,1,1)=="1")d++} END{printf "%.2f", d/(n?n:1)}')
  echo "$m $B as $side: gems(A-B) $out defensive-share $df"
  rm -f $f
done; done
