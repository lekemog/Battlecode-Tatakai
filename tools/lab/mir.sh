#!/bin/bash
# mir.sh CAND BASE [MAPLIST] ; env FUELQ, ROUNDS, JOBS. Output dir $PROJ/m_<CAND>_<BASE><SUFFIX>
C=$1; B=$2; ML=${3:-/root/lab/all.txt}; PROJ=/root/lab
O=$PROJ/m_${C}_${B}${SUFFIX}; rm -rf "$O"; mkdir -p "$O"
rm -rf "$PROJ/bots/$C/.cambc" "$PROJ/bots/$B/.cambc"
while read m; do
  for pr in "$C $B" "$B $C"; do set -- $pr
    echo "$PROJ/bots/$1 $PROJ/bots/$2 $PROJ/maps/$m.map26a $O/${m}_$1_$2.repl26a --statistics $O/${m}_$1_$2.json --json"
  done
done < "$ML" > "$O/manifest.txt"
( cd "$PROJ" && cambc run-batch "$O/manifest.txt" --jobs "${JOBS:-4}" --release --json --timeout 900 --log-limit 600000 ${FUELQ:+--fuel-quantum $FUELQ} ${ROUNDS:+--rounds $ROUNDS} > "$O/batch.log" 2>&1 )
python3 -I /home/user/BattlecodeConversation/tools/lab/mirror_an.py "$C" "$B" "$O" | tee "$PROJ/m_${C}_$B${SUFFIX}.txt" | head -4
[ -n "$KEEP" ] || rm -f "$O"/*.repl26a
