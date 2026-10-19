"""Hourly scrims vs ladder ranks 100-150 and 50-100 with the live bot; record results and download bundles.
usage: scrimloop.py HOURS   (runs until HOURS elapse; safe to restart: state is in data/scrimloop.json)
Each quota window (50 matches = 10 groups/hour): 6 groups from ranks 100-150, 4 from 50-100.
Opponents least-recently scrimmed first; maps rotate through the 17-map pool so every map gets coverage."""
import json, subprocess, os, re, sys, time, random, collections
ME = '9c16b699-cad2-453e-8042-dae23ff934d8'
D = '/home/claude/data'; ST = f'{D}/scrimloop.json'; BUN = f'{D}/bundles_scrim'; os.makedirs(BUN, exist_ok=True)
MAPS = ['rows', 'corners', 'lanes', 'swirl', 'monolith', 'fragment', 'packs', 'collision', 'expanse', 'rushbait_v2',
        'stampede', 'pilgrimage', 'elkring', 'interlock', 'eight', 'contest', 'ambush']
BANDS = [('near', 6), ((100, 150), 4)]   # 19 Oct 16:30: Leke - beat the teams around us first (rank +-40), keep a few vs 100-150
END = time.time() + float(sys.argv[1]) * 3600

def cmd(a, tries=6):
    for t in range(tries):
        r = subprocess.run(a, capture_output=True, text=True)
        if r.returncode == 0: return r.stdout
        msg = r.stderr + r.stdout
        if 'unranked matches an hour' in msg or 'quota' in msg.lower(): return 'QUOTA'
        m = re.search(r'retry after (\d+)', msg); time.sleep(int(m.group(1)) + 1 if m else 5)
    print('FAIL', ' '.join(a[:3]), (r.stderr + r.stdout)[-200:], flush=True); return None

st = json.load(open(ST)) if os.path.exists(ST) else {'groups': [], 'last': {}, 'k': 0}
def save(): json.dump(st, open(ST, 'w'), indent=0)

def ladder():
    T = {}
    for p in (2, 3, 4, 5, 6, 7):   # ranks 51-350
        s = cmd(['cambc', 'ladder', '--page', str(p), '--limit', '50', '--json'])
        if s and s != 'QUOTA':
            for t in json.loads(s)['teams']: T[t['teamId']] = (t['rank'], t['name'], t['rating'])
    return T

def live_bot():
    try: return sorted(json.load(open(f'{D}/submissions.json')), key=lambda s: s['at'])[-1]['bot']
    except Exception: return '?'

def collect():
    for g in st['groups']:
        if g.get('done'): continue
        s = cmd(['cambc', 'match-groups', 'show', g['group'], '--json'])
        if not s or s == 'QUOTA': continue
        ms = json.loads(s)['matches']
        if len(ms) < 5 or any(m['status'] != 'finished' for m in ms): continue
        g['games'] = []
        for m in sorted(ms, key=lambda m: m['position']):
            us = [t for t in m['teams'] if t['teamId'] == ME][0]
            g['games'].append({'id': m['matchId'], 'map': m['map'], 'side': us['side'], 'result': us.get('result')})
            z = f"{BUN}/{m['matchId']}.zip"
            if not os.path.exists(z): cmd(['cambc', 'matches', 'download', m['matchId'], '-o', z])
        g['done'] = True; g['wins'] = sum(x['result'] == 'win' for x in g['games'])
        print('done', g['opp'], g['rank'], f"{g['wins']}/5", ' '.join(f"{x['map']}:{x['result'][0]}" for x in g['games']), flush=True)
    save()

def queue():
    # Leke's rate: 10 groups per hour (6 at ranks 100-150, 4 at 50-99); never take the whole team quota.
    recent = [g for g in st['groups'] if g['at'] >= time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - 3600))]
    if len(recent) >= 10: return 0
    T = ladder()
    if not T: return
    n = 0
    me = 250
    try: me = json.loads(cmd(['cambc', 'match-groups', 'quota', '--json']))['requesterRank']
    except Exception: pass
    for band, want in BANDS:
        lo, hi = (me - 40, me + 40) if band == 'near' else band
        pool = [(tid, v) for tid, v in T.items() if lo <= v[0] <= hi and tid != ME]
        pool.sort(key=lambda kv: (st['last'].get(kv[0], ''), random.random()))
        for tid, (rank, name, rating) in pool[:want]:
            FOCUS = ['contest', 'corners', 'monolith', 'pilgrimage']   # 16:30 UTC 19 Oct: worst maps vs teams within 50 ranks
            OTHER = [m for m in MAPS if m not in FOCUS]
            maps = ','.join(FOCUS + [OTHER[st['k'] % len(OTHER)]])
            s = cmd(['cambc', 'match-groups', 'create', tid, '--maps', maps, '--json'])
            if s == 'QUOTA' or s is None: save(); return n
            st['groups'].append({'group': json.loads(s)['groupId'], 'opp': name, 'opp_id': tid, 'rank': rank, 'rating': round(rating),
                                 'band': ('near' if band == 'near' else f'{lo}-{hi}'), 'maps': maps, 'bot': live_bot(), 'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
            st['last'][tid] = st['groups'][-1]['at']; st['k'] += 1; n += 1
            print('queued', name, rank, maps, flush=True)
    save(); return n

def report():
    bots = sorted({g.get('bot', '?') for g in st['groups'] if g.get('done')}, key=lambda b: max(g['at'] for g in st['groups'] if g.get('bot', '?') == b))
    for bot in bots[-2:]:
        by = collections.defaultdict(lambda: [0, 0]); pm = collections.defaultdict(lambda: [0, 0])
        for g in st['groups']:
            if not g.get('done') or g.get('bot', '?') != bot or (bot == 'v19n' and g['at'] < '2026-10-19T06:40'): continue
            by[g['band']][0] += g['wins']; by[g['band']][1] += 5
            for x in g['games']: pm[x['map']][0] += x['result'] == 'win'; pm[x['map']][1] += 1
        print('REPORT', bot, time.strftime('%H:%MZ', time.gmtime()), ' | '.join(f'{b}: {w}/{n}' for b, (w, n) in sorted(by.items())),
              '|| ' + ' '.join(f'{m} {w}/{n}' for m, (w, n) in sorted(pm.items(), key=lambda kv: kv[1][0] / kv[1][1])), flush=True)

while time.time() < END:
    collect(); queue(); report()
    time.sleep(600)
collect(); report()
