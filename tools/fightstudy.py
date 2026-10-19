"""Altar-fight execution study on a single-altar map from ranked bundles (decode -> measure -> delete).
usage: fightstudy.py MAP [N]
Fight round: a living champion of each side within 5 tiles of the altar. Fights = contiguous runs (gap<=2) of >=3 rounds.
Per side per fight: damage taken (health drops), kills, focus (share of damage taken landing on the single most-hit champion),
ability casts (cooldown jumps from 0), idle-ready rounds (ability off cooldown while an enemy is within 4 tiles), HP at engage."""
import json, os, sys, zipfile, subprocess, tempfile, shutil, statistics as st, collections
D = '/home/claude/data'; MAP = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 30
sys.argv = ['x']; exec(open('/home/claude/tools/replay/dataset.py').read().split('FEATS =')[0])
ALT = load_map(MAP)['altars']
idx = json.load(open(f'{D}/ranked_track.json'))
G = [(k, v) for k, v in idx.items() if v['map'] == MAP and v['at'] >= '2026-10-18T20:20' and os.path.exists(f'{D}/bundles/{k}.zip')][:N]
def d(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
def pos(c): return (c['position']['x'], c['position']['y']) if c.get('position') else None
agg = {res: collections.defaultdict(list) for res in ('win', 'loss')}
for k, v in G:
    tmp = tempfile.mkdtemp(dir=D)
    try: zipfile.ZipFile(f'{D}/bundles/{k}.zip').extractall(tmp)
    except Exception: shutil.rmtree(tmp, ignore_errors=True); continue
    rp = [os.path.join(dp, f) for dp, _, fs in os.walk(tmp) for f in fs if f.endswith('.repl26a')]
    if not rp: shutil.rmtree(tmp, ignore_errors=True); continue
    subprocess.run(['node', '/home/claude/tools/replay/extract.mjs', f'{D}/vis/assets', rp[0], f'{tmp}/r.json'], capture_output=True)
    try: R = json.load(open(f'{tmp}/r.json'))['rounds']
    except Exception: shutil.rmtree(tmp, ignore_errors=True); continue
    shutil.rmtree(tmp, ignore_errors=True)
    us = 0 if v['side'] == 'a' else 1; res = 'win' if v['result'] == 'win' else 'loss'
    fr = []
    for t in range(20, len(R)):
        near = [0, 0]
        for c in R[t]['champions']:
            p = pos(c)
            if c.get('alive') and p and min(d(p, a) for a in ALT) <= 5: near[0 if c['team'] == us else 1] += 1
        if near[0] and near[1]: fr.append(t)
    fights = []; cur = []
    for t in fr:
        if cur and t - cur[-1] > 2:
            if len(cur) >= 3: fights.append(cur)
            cur = []
        cur.append(t)
    if len(cur) >= 3: fights.append(cur)
    A = agg[res]; A['fights'].append(len(fights)); A['games'].append(1)
    for f in fights:
        t0, t1 = f[0], f[-1]
        taken = [collections.Counter(), collections.Counter()]; kills = [0, 0]; casts = [0, 0]; idle = [0, 0]; hp0 = [[], []]
        for c in R[t0]['champions']:
            if c.get('alive'): hp0[0 if c['team'] == us else 1].append(c['health'] / c['maxHealth'])
        for t in range(max(t0, 1), t1 + 1):
            prev = {c['entity']['index']: c for c in R[t - 1]['champions']}
            for c in R[t]['champions']:
                w = 0 if c['team'] == us else 1; p0 = prev.get(c['entity']['index'])
                if not p0: continue
                if p0.get('alive') and c.get('alive') and c['health'] < p0['health']: taken[w][c['entity']['index']] += p0['health'] - c['health']
                if p0.get('alive') and not c.get('alive'): kills[1 - w] += 1; taken[w][c['entity']['index']] += p0['health']
                if c.get('alive'):
                    for j, cd in enumerate(c.get('cooldowns', [])):
                        pcd = (p0.get('cooldowns') or [0, 0])[j] if j < len(p0.get('cooldowns') or []) else 0
                        if cd > pcd and pcd <= 1: casts[w] += 1
                        p = pos(c)
                        if cd == 0 and p and any(o['team'] != c['team'] and o.get('alive') and pos(o) and d(pos(o), p) <= 4 for o in R[t]['champions']): idle[w] += 1
        for w, side in ((0, 'us'), (1, 'them')):
            tot = sum(taken[w].values())
            A[(side, 'dmg_taken')].append(tot); A[(side, 'kills')].append(kills[w]); A[(side, 'casts')].append(casts[w]); A[(side, 'idle')].append(idle[w])
            if tot: A[(side, 'focus_on_them')].append(max(taken[w].values()) / tot)
            if hp0[w]: A[(side, 'hp_engage')].append(st.mean(hp0[w]))
        A['len'].append(len(f)); A['fight_won'].append(sum(taken[0].values()) < sum(taken[1].values()))
for res in ('win', 'loss'):
    A = agg[res]; n = len(A['games'])
    if not n: continue
    m = lambda k: st.mean(A[k]) if A[k] else 0
    print(f"== our {res}s: games {n}, altar fights/game {sum(A['fights']) / n:.1f}, median length {st.median(A['len']) if A['len'] else 0} rounds, fights where we took less damage {100 * m('fight_won'):.0f}%")
    for side in ('us', 'them'):
        print(f"   {side:4}: dmg taken/fight {m((side, 'dmg_taken')):.0f} | kills scored/fight {m((side, 'kills')):.2f} | ability casts/fight {m((side, 'casts')):.1f} | "
              f"idle-ready rounds/fight {m((side, 'idle')):.1f} | damage concentration on the most-hit champ {100 * m((side, 'focus_on_them')):.0f}% | HP at engage {100 * m((side, 'hp_engage')):.0f}%")
