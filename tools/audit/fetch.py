"""Fetch and decode our ranked replays for the match audit.
Order: v16m era (after 2026-10-18T00:37Z), then losses, then the rest. Keeps team stdout logs."""
import json, subprocess, os, time, re, zipfile
ME = '9c16b699-cad2-453e-8042-dae23ff934d8'
OUT = '/home/claude/data/our_rep'; os.makedirs(OUT, exist_ok=True)
def cmd(args):
    for t in range(8):
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode == 0: return r.stdout
        m = re.search(r'retry after (\d+)', r.stderr + r.stdout); time.sleep(int(m.group(1)) + 1 if m else 5)
    return None
allm = []; cur = None
for page in range(12):
    a = ['cambc', 'matches', 'list', '--team', ME, '--kind', 'ranked', '--limit', '100', '--json']
    if cur: a += ['--cursor', cur]
    s = cmd(a)
    if not s: break
    d = json.loads(s); allm += d['matches']; cur = d.get('nextCursor')
    if not cur: break
idx = {}
for m in allm:
    if m['status'] != 'finished': continue
    us = [t for t in m['teams'] if t['teamId'] == ME][0]; op = [t for t in m['teams'] if t['teamId'] != ME][0]
    idx[m['matchId']] = {'map': m['map'], 'side': us['side'], 'result': us.get('result'), 'opp': op['name'], 'at': m['createdAt'],
                         'v16m': m['createdAt'] >= '2026-10-18T00:37'}
json.dump(idx, open(f'{OUT}/index.json', 'w'), indent=0)
order = sorted(idx, key=lambda k: (not idx[k]['v16m'], idx[k]['result'] == 'win', idx[k]['at'][::-1]))
print('matches', len(idx), flush=True)
for mid in order:
    js = f'{OUT}/{mid}.json'
    if os.path.exists(js): continue
    z = f'{OUT}/{mid}.zip'
    if not os.path.exists(z) and cmd(['cambc', 'matches', 'download', mid, '-o', z]) is None: continue
    d = f'{OUT}/{mid}'; os.makedirs(d, exist_ok=True)
    try: zipfile.ZipFile(z).extractall(d)
    except Exception: continue
    rp = [os.path.join(dp, f) for dp, _, fs in os.walk(d) for f in fs if f.endswith('.repl26a')]
    if not rp: continue
    subprocess.run(['node', '/home/claude/tools/replay/extract.mjs', '/home/claude/data/vis/assets', rp[0], js], capture_output=True)
    print(mid, idx[mid]['map'], idx[mid]['result'], os.path.exists(js), sorted(os.listdir(d))[:4], flush=True)
