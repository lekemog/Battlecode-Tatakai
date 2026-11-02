#!/bin/bash
# mirror.sh CAND BASE : paired games CAND vs BASE on every map in $MAPLIST (default $PROJ/all.txt, 70 maps), both sides = 140 games.
# Needs: export PROJ=<cambc project from setup_lab.sh>. Both bots must be in $PROJ/bots (setup_lab.sh copies them from <repo>/bots).
# Output: $PROJ/mirror_<CAND>_<BASE>/ (per-game stats JSON) and a summary: candidate share of decided games, gem margin, per-map table.
# WARNING: the mirror (self-play) PENALISES cautious/escape changes (the weakest-looking caution candidates won on real opponents).
#          Use it for economy / pathing / banking changes and as a no-regression check; judge fight/retreat changes on a panel.
C=${1:?usage: mirror.sh CAND BASE}; B=${2:?}; : "${PROJ:?export PROJ first (see setup_lab.sh)}"
L=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); O=$PROJ/mirror_${C}_$B; rm -rf "$O"; mkdir -p "$O"
rm -rf "$PROJ/bots/$C/.cambc" "$PROJ/bots/$B/.cambc"
while read m; do
  for pr in "$C $B" "$B $C"; do set -- $pr
    echo "$PROJ/bots/$1 $PROJ/bots/$2 $PROJ/maps/$m.map26a $O/${m}_$1_$2.repl26a --statistics $O/${m}_$1_$2.json --json"
  done
done < "${MAPLIST:-$PROJ/all.txt}" > "$O/manifest.txt"
( cd "$PROJ" && cambc run-batch "$O/manifest.txt" --jobs "${JOBS:-2}" --release --json --timeout 900 --log-limit 600000 > "$O/batch.log" 2>&1 )
python3 -I "$L/mirror_an.py" "$C" "$B" "$O" | tee "$PROJ/mirror_${C}_$B.txt" | head -4
rm -f "$O"/*.repl26a
