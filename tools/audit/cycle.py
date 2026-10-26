"""One test cycle: the CURRENT live bot plays unranked groups vs top-100 teams until the hourly quota
is used, then every match is downloaded, decoded and audited.
usage: cycle.py TAG   (TAG e.g. c1_v16o)"""
import json, subprocess, os, time, re, zipfile, sys, random
TAG = sys.argv[1]
ME = '9c16b699-cad2-453e-8042-dae23ff934d8'
OUT = '/home/claude/data/our_rep'
POOL = json.load(open('/home/claude/data/ab/top100_pool.json'))     # [rank, teamId, name], ranks 21-100
LU = '/home/claude/data/ab/cycle_lastused.json'
last = json.load(open(LU)) if os.path.exists(LU) else {}
MAPS = ['rows', 'corners', 'lanes', 'swirl', 'monolith', 'fragment', 'packs', 'collision', 'expanse', 'rushbait_v2',
        'stampede', 'pilgrimage', 'elkring', 'interlock', 'eight', 'contest', 'ambush']
def cmd(args, tries=8):
    for t in range(tries):
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode == 0: return r.stdout
        msg = r.stderr + r.stdout
        if 'unranked matches an hour' in msg: return 'QUOTA'
        m = re.search(r'retry after (\d+)', msg); time.sleep(int(m.group(1)) + 1 if m else 5)
    return None
RESUME = '--resume' in sys.argv
teams = [] if RESUME else sorted(POOL, key=lambda p: (last.get(p[1], ''), random.random()))
groups = json.load(open(f'{OUT}/cycle_{TAG}.json')) if RESUME else []; k = 0
for rank, tid, name in teams:
    maps = ','.join(MAPS[(k * 5 + j) % 17] for j in range(5))
    s = cmd(['cambc', 'match-groups', 'create', tid, '--maps', maps, '--json'])
    if s == 'QUOTA' or s is None: break
    d = json.loads(s); groups.append({'group': d['groupId'], 'opp': name, 'rank': rank, 'maps': maps})
    last[tid] = time.strftime('%Y-%m-%dT%H:%M:%S'); k += 1
    print('queued', name, rank, maps, flush=True)
if not RESUME:
    json.dump(last, open(LU, 'w'))
    json.dump(groups, open(f'{OUT}/cycle_{TAG}.json', 'w'))
# wait for completion
pending = {g['group'] for g in groups}; matches = {}
while pending:
    time.sleep(45)
    for g in list(pending):
        s = cmd(['cambc', 'match-groups', 'show', g, '--json'], tries=3)
        if not s or s == 'QUOTA': continue
        d = json.loads(s); ms = d.get('matches', [])
        if ms and all(m['status'] == 'finished' for m in ms):
            pending.discard(g)
            for m in ms:
                us = [t for t in m['teams'] if t['teamId'] == ME][0]; op = [t for t in m['teams'] if t['teamId'] != ME][0]
                matches[m['matchId']] = {'map': m['map'], 'side': us['side'], 'result': us.get('result'), 'opp': op['name'],
                                         'at': m['createdAt'], 'v16m': False, 'cycle': TAG}
print('finished', len(matches), 'wins', sum(v['result'] == 'win' for v in matches.values()), flush=True)
idx = json.load(open(f'{OUT}/index.json')); idx.update(matches); json.dump(idx, open(f'{OUT}/index.json', 'w'))
for mid in matches:
    js = f'{OUT}/{mid}.json'
    if os.path.exists(js): continue
    z = f'{OUT}/{mid}.zip'
    if cmd(['cambc', 'matches', 'download', mid, '-o', z]) in (None, 'QUOTA'): continue
    dd = f'{OUT}/{mid}'; os.makedirs(dd, exist_ok=True)
    try: zipfile.ZipFile(z).extractall(dd)
    except Exception: continue
    rp = [os.path.join(a, f) for a, _, fs in os.walk(dd) for f in fs if f.endswith('.repl26a')]
    if rp: subprocess.run(['node', '/home/claude/tools/replay/extract.mjs', '/home/claude/data/vis/assets', rp[0], js], capture_output=True)
print('decoded', sum(os.path.exists(f'{OUT}/{m}.json') for m in matches), flush=True)
r = subprocess.run(['python3', '-I', '/home/claude/tools/audit/audit.py', '--cycle', TAG], capture_output=True, text=True)
open(f'{OUT}/cycle_{TAG}_audit.txt', 'w').write(r.stdout + r.stderr)
print(r.stdout)
