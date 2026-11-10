#!/bin/bash
# setup_lab.sh PROJ_DIR [bot ...]
# Creates (or refreshes) a cambc project in PROJ_DIR for local testing: SDK, the current map pool (128 maps on patch 4.0.0), the 7 bench opponents, and the given
# bots from <repo>/bots/. Prints the exports to use. Safe to rerun.
set -e
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
PROJ=${1:?usage: setup_lab.sh PROJ_DIR [bot ...]}; shift || true
mkdir -p "$PROJ"; PROJ=$(cd "$PROJ" && pwd)
if [ ! -f "$PROJ/cambc.toml" ]; then ( cd "$PROJ" && cambc init . --yes >/dev/null 2>&1 || echo "NOTE: cambc init failed; run it by hand (cambc init . --yes) and check 'cambc --version' is 4.0.0" ); fi
( cd "$PROJ" && cambc maps pull >/dev/null 2>&1 || echo "NOTE: 'cambc maps pull' needs 'cambc login'; falling back to the maps bundled with the SDK/bench" )
mkdir -p "$PROJ/bots" "$PROJ/maps"
[ "$(ls "$PROJ"/maps/*.map26a 2>/dev/null | wc -l)" -ge 120 ] || cp -n "$REPO"/maps/*.map26a "$PROJ/maps/" 2>/dev/null || true   # the repo bundles the current 128-map pool
for b in "$REPO"/bench/bots/*; do rm -rf "$PROJ/bots/$(basename "$b")"; cp -r "$b" "$PROJ/bots/"; done
for b in "$@"; do
  [ -d "$REPO/bots/$b" ] || { echo "no such bot folder: $REPO/bots/$b"; continue; }
  rm -rf "$PROJ/bots/$b"; cp -r "$REPO/bots/$b" "$PROJ/bots/$b"
done
rm -rf "$PROJ"/bots/*/.cambc          # ALWAYS: a copied build cache makes cambc reuse the wrong binary
# all.txt = the official map names (from the platform when signed in), restricted to maps that exist as files
( cd "$PROJ" && for pg in 1 2 3; do cambc maps list --page $pg --limit 50 --json 2>/dev/null; done | python3 -c "
import json,sys
dec=json.JSONDecoder(); s=sys.stdin.read(); i=0; names=[]
while i<len(s):
    while i<len(s) and s[i].isspace(): i+=1
    if i>=len(s): break
    o,j=dec.raw_decode(s,i); i=j
    names+=[m['name'] for m in (o if isinstance(o,list) else (o.get('maps') or o.get('items') or []))]
print('\n'.join(sorted(set(names))))" ) > "$PROJ/official.txt"
if [ "$(wc -l < "$PROJ/official.txt")" -ge 60 ]; then
  # platform names use underscores (00gem_fields); the files use hyphens for some of them (00gem-fields.map26a): accept either
  while read m; do h=${m//_/-}; if [ -f "$PROJ/maps/$m.map26a" ]; then echo "$m"; elif [ -f "$PROJ/maps/$h.map26a" ]; then echo "$h"; fi; done < "$PROJ/official.txt" | sort -u > "$PROJ/all.txt"
else
  echo "NOTE: could not list the official maps (not signed in?); using every map file under maps/ - check for duplicates"
  ( cd "$PROJ/maps" && ls *.map26a | sed 's/\.map26a$//' | sort ) > "$PROJ/all.txt"
fi
echo "maps: $(wc -l < "$PROJ/all.txt") (list in $PROJ/all.txt); bots: $(ls "$PROJ/bots" | tr '\n' ' ')"
echo "export PROJ=$PROJ REPO=$REPO"
