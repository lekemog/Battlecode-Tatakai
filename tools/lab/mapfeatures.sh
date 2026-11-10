#!/bin/bash
# mapfeatures.sh : one CSV row of map features per map in $MAPLIST (default $PROJ/all.txt), using bots/maprobe (needs $PROJ from setup_lab.sh).
# Columns: map,w,h,groups,gold,gems,altars,walls,wolf,elk,gemcl,goldcl,mono,golem. Output: $PROJ/mapfeatures.csv
: "${PROJ:?export PROJ first}"; REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
rm -rf "$PROJ/bots/maprobe"; cp -r "$REPO/bots/maprobe" "$PROJ/bots/maprobe"; rm -rf "$PROJ/bots/maprobe/.cambc"
O=$PROJ/mapfeat; rm -rf "$O"; mkdir -p "$O"
while read m; do echo "$PROJ/bots/maprobe $PROJ/bots/maprobe $PROJ/maps/$m.map26a $O/$m.repl26a --json"; done < "${MAPLIST:-$PROJ/all.txt}" > "$O/manifest.txt"
( cd "$PROJ" && cambc run-batch "$O/manifest.txt" --jobs "${JOBS:-2}" --release --json --timeout 300 --rounds 3 > "$O/batch.log" 2>&1 )
echo "map,w,h,groups,gold,gems,altars,walls,wolf,elk,gemcl,goldcl,mono,golem" > "$PROJ/mapfeatures.csv"
python3 -I - "$O" >> "$PROJ/mapfeatures.csv" <<'PY'
import sys,glob,os,re,zipfile
for f in sorted(glob.glob(sys.argv[1]+'/*.repl26a')):
    m=os.path.basename(f)[:-len('.repl26a')]
    try: raw=zipfile.ZipFile(f).read('team-a.stdout').decode('utf-8','replace').replace('\x00','')
    except Exception: continue
    l=next((x for x in raw.split('\n') if 'MAPINFO' in x and 'err' not in x),None)
    if not l: continue
    d=re.search(r'(\d+)x(\d+)',l); kv=dict(re.findall(r'(\w+)=(\d+)',l))
    print(','.join([m,d.group(1),d.group(2)]+[kv.get(k,'0') for k in 'groups gold gems altars walls wolf elk gemcl goldcl mono golem'.split()]))
PY
rm -f "$O"/*.repl26a; echo "rows: $(($(wc -l < "$PROJ/mapfeatures.csv")-1)) -> $PROJ/mapfeatures.csv"
