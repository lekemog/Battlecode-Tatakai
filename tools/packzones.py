"""Packs zone-time: share of alive champion-rounds within 3 tiles of home 44s / central 48s, and team spread.
usage: packzones.py BOT [BOT...]   (reads decoded scrims in data/scrim_rep; run tools/behav.py packs first)"""
import json, sys, collections, statistics as st
idx = json.load(open('/home/claude/data/scrim_rep/index.json'))
G = {'home44a': [(8, 2), (16, 2)], 'home44b': [(22, 28), (14, 28)], 'c48': [(12, 18), (18, 12)]}
for bot in sys.argv[1:]:
    tot = [collections.Counter(), collections.Counter()]; sp = [[], []]; n = 0
    for k, v in idx.items():
        if v['map'] != 'packs' or v.get('bot', 'v19n') != bot: continue
        try: R = json.load(open(f'/home/claude/data/scrim_rep/{k}.json'))['rounds']
        except Exception: continue
        n += 1; us = 0 if v['side'] == 'a' else 1
        for t in range(20, min(len(R), 500), 2):
            for w in (0, 1):
                team = us if w == 0 else 1 - us; own = 'a' if team == 0 else 'b'
                P = [(c['position']['x'], c['position']['y']) for c in R[t]['champions'] if c['team'] == team and c.get('alive') and c.get('position')]
                for p in P:
                    lab = 'other'
                    for name, cs in G.items():
                        if any(max(abs(p[0] - x), abs(p[1] - y)) <= 3 for x, y in cs):
                            lab = 'home44' if name == 'home44' + own else ('c48' if name == 'c48' else 'enemy44'); break
                    tot[w][lab] += 1
                if len(P) >= 2: sp[w].append(max(max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a in P for b in P))
    for w, nm in ((0, 'us'), (1, 'them')):
        s = sum(tot[w].values()) or 1
        print(f'{bot} n={n} {nm}: ' + ' '.join(f'{k} {round(100 * c / s)}%' for k, c in tot[w].most_common()) + f' | spread {st.median(sp[w]) if sp[w] else "-"}')
