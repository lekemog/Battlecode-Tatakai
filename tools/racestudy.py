"""Score race + bag losses + first deaths for one map from scrim bundles (decode -> analyse -> delete).
usage: racestudy.py MAP BOT [N]
Prints: submitted-gem gap by round (median over games), deaths carrying gems (distance to nearest altar, logged action),
and the first 3 deaths per loss classified like the contest study."""
import json, os, sys, zipfile, subprocess, statistics as st, tempfile, shutil, re, collections
D = '/home/claude/data'; MAP, BOT = sys.argv[1], sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 20
sys.argv = ['x']; exec(open('/home/claude/tools/replay/dataset.py').read().split('FEATS =')[0])
M = load_map(MAP); ALT = M.get('altars', [])
S = json.load(open(f'{D}/scrimloop.json'))
games = [(g, x) for g in S['groups'] if g.get('done') and g.get('bot') == BOT and (BOT != 'v19n' or g['at'] >= '2026-10-19T06:40') for x in g['games'] if x['map'] == MAP][-N:]
def d(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
race = collections.defaultdict(list); bag = []; first = collections.Counter(); firstrows = []; n = 0; wins = 0
gemsby = collections.Counter(); lostby = collections.Counter()
for g, x in games:
    z = f'{D}/bundles_scrim/{x["id"]}.zip'
    if not os.path.exists(z): continue
    tmp = tempfile.mkdtemp(dir=D); zipfile.ZipFile(z).extractall(tmp)
    subprocess.run(['node', '/home/claude/tools/replay/extract.mjs', f'{D}/vis/assets', f'{tmp}/replay.repl26a', f'{tmp}/r.json'], capture_output=True)
    try: R = json.load(open(f'{tmp}/r.json'))['rounds']
    except Exception: shutil.rmtree(tmp, ignore_errors=True); continue
    txt = open(f'{tmp}/team-a.stdout', errors='ignore').read() if os.path.exists(f'{tmp}/team-a.stdout') else ''
    logs = collections.defaultdict(list)
    for r, s, m, _ in re.findall(r'T (\d+) (\d) (\w+) (-?\d+) ', txt): logs[int(s)].append((int(r), m))
    n += 1; us = 0 if x['side'] == 'a' else 1; won = x['result'] == 'win'; wins += won
    for t in range(100, 1001, 100):
        if t < len(R): race[t].append(R[t]['submittedGems'][us] - R[t]['submittedGems'][1 - us])
    ours = [c['entity']['index'] for c in R[20]['champions'] if c['team'] == us]; slot = {e: i for i, e in enumerate(ours)}
    prev = {c['entity']['index']: c for c in R[20]['champions']}; k = 0
    for t in range(21, len(R)):
        cur = {c['entity']['index']: c for c in R[t]['champions']}
        for c0 in prev.values():
            c1 = cur.get(c0['entity']['index'])
            if not c1 or not c0.get('alive') or c1.get('alive'): continue
            w = 0 if c0['team'] == us else 1; gm = c0.get('gems') or 0
            if gm: lostby[w] += gm
            if w != 0: continue
            p = (c0['position']['x'], c0['position']['y']); e = c0['entity']['index']
            acts = [m for r, m in logs.get(slot.get(e, -1), []) if t - 12 <= r <= t]
            if gm >= 20: bag.append((t, gm, min(d(p, a) for a in ALT) if ALT else -1, '>'.join(acts[-3:])))
            if not won and k < 3:
                en = sum(1 for c in R[t - 1]['champions'] if c['team'] != us and c.get('alive') and c.get('position') and d((c['position']['x'], c['position']['y']), p) <= 5)
                al = sum(1 for c in R[t - 1]['champions'] if c['team'] == us and c['entity']['index'] != e and c.get('alive') and c.get('position') and d((c['position']['x'], c['position']['y']), p) <= 5)
                c5 = next((c for c in R[max(0, t - 6)]['champions'] if c['entity']['index'] == e), c0)
                last = acts[-1] if acts else '?'
                cls = ('died retreating/evading' if last in ('retreat', 'evade') else 're-entered after retreat') if ('retreat' in acts or 'evade' in acts) else \
                      ('bank walk/channel' if last in ('bank', 'tribute') or gm >= 40 else ('lone, caught' if al == 0 else 'group fight'))
                first[cls] += 1; firstrows.append((t, round(c5['health'] / c5['maxHealth'], 2), al, en, gm, last)); k += 1
        prev = cur
    shutil.rmtree(tmp, ignore_errors=True)
print(f'{MAP} {BOT}: games {n} wins {wins}')
print('submitted-gem gap us-them by round (median):', {t: st.median(v) for t, v in sorted(race.items()) if v})
print(f'gems lost on death per game: us {lostby[0] / max(1, n):.0f} them {lostby[1] / max(1, n):.0f}')
if bag:
    print(f'our deaths carrying >=20 gems: {len(bag)} ({len(bag) / n:.1f}/game), median bag {st.median(b[1] for b in bag)}, median dist to altar {st.median(b[2] for b in bag)}')
    print('   last actions:', collections.Counter(b[3].split('>')[-1] if b[3] else '?' for b in bag).most_common(6))
if firstrows:
    print('first 3 deaths in losses:', first.most_common())
    print('   median round', st.median(r[0] for r in firstrows), '| HP 5 rounds before', st.median(r[1] for r in firstrows), '| allies/enemies within 5', st.median(r[2] for r in firstrows), '/', st.median(r[3] for r in firstrows))
