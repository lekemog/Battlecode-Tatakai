"""Whole-day audit of our ranked games: decode each bundle -> compact per-game metrics -> delete.
usage: dayaudit.py SINCE [MAX]   writes data/dayaudit.json (cached; resumable)
Per game, us/them: gold@150/300/600 (team earned), gems submitted @200/400/600 and final, deaths, gems lost on death,
mean HP fraction when entering fights near altars, max HP @300, first death round, rounds, bank count & median bag,
champion-time dead %, kills."""
import json, os, sys, zipfile, subprocess, tempfile, shutil, statistics as st
D = '/home/claude/data'; SINCE = sys.argv[1]; MAX = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
OUT = f'{D}/dayaudit.json'; cache = json.load(open(OUT)) if os.path.exists(OUT) else {}
idx = json.load(open(f'{D}/ranked_track.json'))
G = sorted(((k, v) for k, v in idx.items() if v['at'] >= SINCE and os.path.exists(f'{D}/bundles/{k}.zip')), key=lambda kv: kv[1]['at'])[:MAX]
n = 0
for k, v in G:
    if k in cache: continue
    tmp = tempfile.mkdtemp(dir=D)
    try:
        zipfile.ZipFile(f'{D}/bundles/{k}.zip').extractall(tmp)
        rp = [os.path.join(dp, f) for dp, _, fs in os.walk(tmp) for f in fs if f.endswith('.repl26a')][0]
        subprocess.run(['node', '/home/claude/tools/replay/extract.mjs', f'{D}/vis/assets', rp, f'{tmp}/r.json'], capture_output=True, timeout=300)
        R = json.load(open(f'{tmp}/r.json'))['rounds']
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True); continue
    shutil.rmtree(tmp, ignore_errors=True)
    us = 0 if v['side'] == 'a' else 1; T = len(R) - 1
    def team(t, w): tm = us if w == 0 else 1 - us; return [c for c in R[min(t, T)]['champions'] if c['team'] == tm]
    gold = {t: [sum(c.get('earnedGold', 0) for c in team(t, w)) for w in (0, 1)] for t in (150, 300, 600)}
    gems = {t: [R[min(t, T)]['submittedGems'][us], R[min(t, T)]['submittedGems'][1 - us]] for t in (200, 400, 600)}
    dead = [0, 0]; lost = [0, 0]; first = [None, None]; deadrounds = [0, 0]; alive = [0, 0]; banks = [[], []]
    prev = {}; pa = {}
    for t in range(15, len(R)):
        for c in R[t]['champions']:
            i = c['entity']['index']; w = 0 if c['team'] == us else 1; gm = c.get('gems') or 0
            if pa.get(i) and not c.get('alive'):
                dead[w] += 1; lost[w] += prev.get(i, 0)
                if first[w] is None: first[w] = t
            if c.get('alive'):
                alive[w] += 1
                if i in prev and gm < prev[i]: banks[w].append(prev[i])
            else: deadrounds[w] += 1
            pa[i] = c.get('alive'); prev[i] = gm if c.get('alive') else 0
    cache[k] = {'map': v['map'], 'res': v['result'], 'bot': v['bot'], 'opp': v['opp'], 'opp_id': v['opp_id'], 'at': v['at'], 'rounds': len(R),
                'gold': gold, 'gems': gems, 'final': [R[T]['submittedGems'][us], R[T]['submittedGems'][1 - us]],
                'deaths': dead, 'lost': lost, 'first': first, 'deadpct': [100 * deadrounds[w] / max(1, deadrounds[w] + alive[w]) for w in (0, 1)],
                'hp300': [st.mean(c['maxHealth'] for c in team(300, w)) if team(300, w) else 0 for w in (0, 1)],
                'banks': [len(banks[w]) for w in (0, 1)], 'bag': [st.median(banks[w]) if banks[w] else 0 for w in (0, 1)]}
    n += 1
    if n % 10 == 0: json.dump(cache, open(OUT, 'w')); print('done', n, flush=True)
json.dump(cache, open(OUT, 'w')); print('total cached', len(cache))
