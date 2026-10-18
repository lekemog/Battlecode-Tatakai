"""Paired top-100 test: each bot plays the SAME fresh top-100 opponents on the same maps, one bot
at a time (scrims use the live submission). usage: paired.py TAG botA,botB [N_opps] [--keep BOT]
Writes cycle_<TAG>_<bot>.json group lists, waits per bot, then downloads+audits via cycle.py --resume."""
import json, subprocess, os, time, re, sys, random
TAG = sys.argv[1]; BOTS = sys.argv[2].split(','); N = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 30 // len(BOTS)
KEEP = sys.argv[sys.argv.index('--keep') + 1] if '--keep' in sys.argv else BOTS[-1]
OUT = '/home/claude/data/our_rep'
POOL = json.load(open('/home/claude/data/ab/top100_pool.json'))
LU = '/home/claude/data/ab/cycle_lastused.json'; last = json.load(open(LU)) if os.path.exists(LU) else {}
MAPS = ['rows', 'corners', 'lanes', 'swirl', 'monolith', 'fragment', 'packs', 'collision', 'expanse', 'rushbait_v2',
        'stampede', 'pilgrimage', 'elkring', 'interlock', 'eight', 'contest', 'ambush']
def cmd(args, tries=8, cwd=None):
    for t in range(tries):
        r = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
        if r.returncode == 0: return r.stdout
        msg = r.stderr + r.stdout
        if 'unranked matches an hour' in msg: return 'QUOTA'
        m = re.search(r'retry after (\d+)', msg); time.sleep(int(m.group(1)) + 1 if m else 5)
    return None
opps = sorted(POOL, key=lambda p: (last.get(p[1], ''), random.random()))[:N]
off = random.randrange(17)
plan = [(rank, tid, name, ','.join(MAPS[(off + k * 5 + j) % 17] for j in range(5))) for k, (rank, tid, name) in enumerate(opps)]
for b in BOTS:
    print(cmd(['cambc', 'submit', f'bots/{b}'], cwd='/home/claude/proj').strip().split('\n')[-1], flush=True)
    time.sleep(90)
    groups = []
    for rank, tid, name, maps in plan:
        for attempt in range(60):
            s = cmd(['cambc', 'match-groups', 'create', tid, '--maps', maps, '--json'])
            if s and s != 'QUOTA': break
            print('quota wait', flush=True); time.sleep(120)
        d = json.loads(s); groups.append({'group': d['groupId'], 'opp': name, 'rank': rank, 'maps': maps})
        last[tid] = time.strftime('%Y-%m-%dT%H:%M:%S'); print(b, 'queued', name, rank, maps, flush=True)
    json.dump(last, open(LU, 'w')); json.dump(groups, open(f'{OUT}/cycle_{TAG}_{b}.json', 'w'))
    pending = {g['group'] for g in groups}
    while pending:
        time.sleep(45)
        for g in list(pending):
            s = cmd(['cambc', 'match-groups', 'show', g, '--json'], tries=3)
            if not s or s == 'QUOTA': continue
            ms = json.loads(s).get('matches', [])
            if ms and all(m['status'] == 'finished' for m in ms): pending.discard(g)
    print(b, 'all finished', flush=True)
if KEEP != BOTS[-1]: print(cmd(['cambc', 'submit', f'bots/{KEEP}'], cwd='/home/claude/proj').strip().split('\n')[-1], flush=True)
for b in BOTS:
    subprocess.run(['python3', '-I', '/home/claude/tools/audit/cycle.py', f'{TAG}_{b}', '--resume'])
