"""Download top-vs-top replays (map-balanced) and extract per-round JSON."""
import json, subprocess, os, time, re, collections, random
TM = json.load(open('/home/claude/data/top/topmatches.json'))
top = json.load(open('/home/claude/data/top/top.json'))
R = '/home/claude/data/rep'
by = collections.defaultdict(list)
for mid, m in TM.items():
    rk = max(top[t['teamId']] for t in m['teams'])
    by[m['map']].append((rk, mid))
order = []
for k in by: by[k].sort()
for i in range(10):
    for k in sorted(by):
        if i < len(by[k]): order.append((by[k][i][1], k))
meta = {}
MF = f'{R}/meta.json'
if os.path.exists(MF): meta = json.load(open(MF))
for mid, mp in order:
    js = f'{R}/json/{mid}.json'
    if os.path.exists(js): continue
    z = f'{R}/{mid}.zip'
    for t in range(8):
        r = subprocess.run(['cambc', 'matches', 'download', mid, '-o', z], capture_output=True, text=True)
        if os.path.exists(z): break
        m = re.search(r'retry after (\d+)', r.stderr + r.stdout); time.sleep(int(m.group(1)) + 1 if m else 5)
    if not os.path.exists(z): continue
    d = f'{R}/{mid}'
    subprocess.run(['unzip', '-o', '-q', z, '-d', d])
    subprocess.run(['node', '/home/claude/tools/replay/extract.mjs', '/home/claude/data/vis/assets', f'{d}/replay.repl26a', js], capture_output=True)
    m = TM[mid]
    meta[mid] = {'map': mp, 'teams': {t['side']: {'name': t['name'], 'rank': top[t['teamId']], 'result': t.get('result')} for t in m['teams']}}
    json.dump(meta, open(MF, 'w'))
    print(mid, mp, os.path.exists(js), flush=True)
