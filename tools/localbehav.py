"""Local behaviour check: run CAND vs opponents on one map (both sides), keep and decode replays, run mapstudy.
usage: localbehav.py CAND MAPNAME OPP1,OPP2,..."""
import sys, os, json, subprocess, time
cand, mname, opps = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
mid = [m['id'] for m in json.load(open('/home/claude/data/maps_index.json')) if m['name'] == mname][0][:8]
PROJ = '/home/claude/proj'; out = f'/home/claude/data/lb_{cand}_{mname}'
subprocess.run(['rm', '-rf', out]); os.makedirs(out)
rows = []
with open(f'{out}/manifest.txt', 'w') as f:
    for o in opps:
        for a, b in ((cand, o), (o, cand)):
            tag = f'{a}__{b}'; rows.append((tag, 'a' if a == cand else 'b', o))
            f.write(f'{PROJ}/bots/{a} {PROJ}/bots/{b} {PROJ}/maps/p_{mid}.map26a {out}/{tag}.repl26a --statistics {out}/{tag}.stats --json\n')
subprocess.run(['cambc', 'run-batch', f'{out}/manifest.txt', '--jobs', '2', '--release', '--json', '--timeout', '900'], cwd=PROJ,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
idx = {}
for tag, side, o in rows:
    if not os.path.exists(f'{out}/{tag}.repl26a'): continue
    import zipfile
    rp = f'{out}/{tag}.repl26a'
    if zipfile.is_zipfile(rp):
        d = f'{out}/{tag}'; os.makedirs(d, exist_ok=True); zipfile.ZipFile(rp).extractall(d)
        rp = [os.path.join(dp, x) for dp, _, fs in os.walk(d) for x in fs if x.endswith('.repl26a')][0]
    subprocess.run(['node', '/home/claude/tools/replay/extract.mjs', '/home/claude/data/vis/assets', rp, f'{out}/{tag}.json'], capture_output=True)
    st = json.load(open(f'{out}/{tag}.stats')); won = st['match']['outcome'] == ('teamA' if side == 'a' else 'teamB')
    idx[tag] = {'map': mname, 'side': side, 'result': 'win' if won else 'loss', 'opp': o, 'at': '', 'v16m': True}
    pass
json.dump(idx, open(f'{out}/index.json', 'w'))
ms = open('/home/claude/tools/audit/mapstudy.py').read().replace('/home/claude/data/our_rep', out)
r = subprocess.run(['python3', '-I', '-c', ms, mname], capture_output=True, text=True)
print(cand, mname); print('\n'.join(l for l in (r.stdout + r.stderr[-500:]).split('\n') if 'opp drafts' not in l))
