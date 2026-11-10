#!/bin/bash
# smoke.sh BOT [map ...] : 2000-round games of BOT vs x_daniel8 (non-release, traces kept) on the given maps (default 02the-pack 01islands).
# Prints result, engine-error counts ('not in vision' = error 97, 'bot error' lines) and fuel-outs. A clean bot has 0 other errors.
B=${1:?usage: smoke.sh BOT [map ...]}; shift; : "${PROJ:?export PROJ first}"; cd "$PROJ"
rm -rf "bots/$B/.cambc"
for M in ${@:-02the-pack 01islands}; do
  D=smoke_${B}_$M; rm -rf "$D"
  timeout 1500 cambc run "$B" x_daniel8 --map "$M" --rounds 2000 -o "$D" > "$D.log" 2>&1
  f=$(ls "$D"/*.repl26a 2>/dev/null | head -1); [ -n "$f" ] && unzip -p "$f" team-a.stdout 2>/dev/null | tr -d '\000' > "$D.out"
  echo "== $B $M: $(grep -a -i 'wins\|draw' "$D.log" | head -1)"
  echo "   not-in-vision=$(grep -ac 'not in vision' "$D.out" 2>/dev/null) other-bot-errors=$(grep -a 'bot error' "$D.out" 2>/dev/null | grep -vac 'not in vision') fuel-outs=$(grep -aic 'out of fuel' "$D.log" "$D.out" 2>/dev/null | tr '\n' ' ')"
done
