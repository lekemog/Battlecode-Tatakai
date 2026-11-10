#!/bin/bash
# profsweep.sh OUTDIR [map ...] : run the v51p profiler build (bots/v51p in $PROJ) on maps, both sides, vs x_daniel8 and v50p1;
# BOT=v51q selects another profiled bot (default v51p). Keeps only the P/G/L/D lines of the profiled team (OUTDIR/<map>_<opp>_<side>.prof). Analyse with tools/lab/profreport.py.
BOT=${BOT:-v51p}; export BOT; O=${1:?usage: profsweep.sh OUTDIR [map...]}; shift; : "${PROJ:?export PROJ}"; mkdir -p "$O"
MAPS=${@:-"00ambush 01big-world 02the-pack 03the-front 00contest 00expanse 00rows 01fracture 00lanes 02fields 00eight 00packs 01islands 00stampede 03colosseum 02cuts"}
run() { m=$1; opp=$2; side=$3; d=$(mktemp -d); cd "$PROJ"
  if [ $side = a ]; then cambc run bots/$BOT bots/$opp --map maps/$m.map26a --release -o $d >/dev/null 2>&1; t=team-a.stdout
  else cambc run bots/$opp bots/$BOT --map maps/$m.map26a --release -o $d >/dev/null 2>&1; t=team-b.stdout; fi
  f=$(ls $d/*.repl26a 2>/dev/null | head -1); [ -n "$f" ] && unzip -p $f $t | tr -d '\000' | grep -a "^[PGLD] r\|^field cost" > "$O/${m}_${opp}_$side.prof"
  [ -n "$f" ] && unzip -p $f replay.repl26a >/dev/null 2>&1; rm -rf $d; }
export -f run; export PROJ O BOT
for m in $MAPS; do for opp in x_daniel8 v50p1; do for s in a b; do echo "$m $opp $s"; done; done; done | xargs -P 4 -L 1 bash -c 'run $0 $1 $2'
echo done > "$O/DONE"
