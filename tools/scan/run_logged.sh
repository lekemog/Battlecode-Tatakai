#!/usr/bin/env bash
# Play BOT against the 7 bench opponents on every bench map (both sides) and KEEP the replay bundles (with our
# stdout traces) and statistics, for tools/scan/scan.py. bench/bench.py deletes the bundles, so it can't be used.
# usage: PROJ=<cambc project> OUT=<dir> [JOBS=4] [MAPS=a,b] tools/scan/run_logged.sh BOT [OPP,OPP..]
set -euo pipefail
BOT=$1
OPPS=${2:-x_daniel8,x_de41h4,h_mohnish,h_deysag,h_vatsal,h_photon,h_apex}
REPO=$(cd "$(dirname "$0")/../.." && pwd)
MAPS=${MAPS:-$(cat "$REPO/bench/pool6.txt")}
mkdir -p "$OUT"
MAN="$OUT/manifest.txt"; : > "$MAN"
IFS=',' read -ra OL <<< "$OPPS"; IFS=',' read -ra ML <<< "$MAPS"
for o in "${OL[@]}"; do for m in "${ML[@]}"; do
  echo "$PROJ/bots/$BOT $PROJ/bots/$o $PROJ/maps/$m.map26a $OUT/${m}_${BOT}_${o}.repl26a --statistics $OUT/${m}_${BOT}_${o}.json --json" >> "$MAN"
  echo "$PROJ/bots/$o $PROJ/bots/$BOT $PROJ/maps/$m.map26a $OUT/${m}_${o}_${BOT}.repl26a --statistics $OUT/${m}_${o}_${BOT}.json --json" >> "$MAN"
done; done
cd "$PROJ" && cambc run-batch "$MAN" --jobs "${JOBS:-4}" --release --json --timeout 900 > "$OUT/run.log" 2>&1 || true
echo "$(ls "$OUT"/*.repl26a 2>/dev/null | wc -l) bundles in $OUT"
