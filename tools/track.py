"""Track our ranked matches: refresh the index, download match bundles (zip) for new matches, print a record per bot version.
usage: track.py [--since ISO] [--no-download]
Index: /home/claude/data/ranked_track.json   Bundles: /home/claude/data/bundles/<matchId>.zip
The bot version is inferred from data/submissions.json (the latest submission made before the match was created)."""
import json, subprocess, os, re, sys, time, collections
ME = '9c16b699-cad2-453e-8042-dae23ff934d8'
D = '/home/claude/data'; IDX = f'{D}/ranked_track.json'; BUN = f'{D}/bundles'; os.makedirs(BUN, exist_ok=True)
args = sys.argv[1:]
since = args[args.index('--since') + 1] if '--since' in args else '2026-10-18T20:19'
download = '--no-download' not in args

def cmd(a):
    for t in range(8):
        r = subprocess.run(a, capture_output=True, text=True)
        if r.returncode == 0: return r.stdout
        m = re.search(r'retry after (\d+)', r.stderr + r.stdout); time.sleep(int(m.group(1)) + 1 if m else 5)
    return None

idx = json.load(open(IDX)) if os.path.exists(IDX) else {}
subs = sorted(json.load(open(f'{D}/submissions.json')), key=lambda s: s['at'])
def bot_at(t):
    b = '?'
    for s in subs:
        if s['at'] <= t[:16]: b = s['bot']
    return b

cur = None; new = 0
for page in range(30):
    a = ['cambc', 'matches', 'list', '--team', ME, '--kind', 'ranked', '--limit', '100', '--json']
    if cur: a += ['--cursor', cur]
    s = cmd(a)
    if not s: break
    d = json.loads(s); stop = False
    for m in d['matches']:
        if m['createdAt'] < since: stop = True; continue
        if m['status'] != 'finished': continue
        us = [t for t in m['teams'] if t['teamId'] == ME][0]; op = [t for t in m['teams'] if t['teamId'] != ME][0]
        if m['matchId'] not in idx: new += 1
        idx[m['matchId']] = {'at': m['createdAt'], 'group': m['groupId'], 'pos': m.get('position'), 'map': m['map'],
                             'side': us['side'], 'result': us.get('result'), 'opp': op['name'], 'opp_id': op['teamId'],
                             'opp_picks': op.get('draftPicks'), 'bot': bot_at(m['createdAt'])}
    cur = d.get('nextCursor')
    if stop or not cur: break
json.dump(idx, open(IDX, 'w'), indent=0)

if download:
    got = 0
    for mid in sorted(idx, key=lambda k: idx[k]['at'], reverse=True):
        z = f'{BUN}/{mid}.zip'
        if os.path.exists(z) and os.path.getsize(z) > 0: continue
        if cmd(['cambc', 'matches', 'download', mid, '-o', z]) is not None: got += 1
    print('bundles downloaded', got, 'total', len(os.listdir(BUN)))

print('index', len(idx), 'new', new)
by = collections.defaultdict(list)
for m in idx.values(): by[m['bot']].append(m)
for b, L in sorted(by.items(), key=lambda kv: min(m['at'] for m in kv[1])):
    w = sum(m['result'] == 'win' for m in L)
    G = collections.defaultdict(list)
    for m in L: G[m['group']].append(m['result'] == 'win')
    gw = sum(sum(v) * 2 > len(v) for v in G.values() if len(v) == 5)
    full = sum(len(v) == 5 for v in G.values())
    print(f'{b}: games {w}/{len(L)} ({100*w/max(1,len(L)):.0f}%)  groups won {gw}/{full}  first {min(m["at"] for m in L)[:16]}')
    pm = collections.defaultdict(lambda: [0, 0])
    for m in L: pm[m['map']][0] += m['result'] == 'win'; pm[m['map']][1] += 1
    print('   ' + '  '.join(f'{k} {v[0]}/{v[1]}' for k, v in sorted(pm.items(), key=lambda kv: -kv[1][1])))
