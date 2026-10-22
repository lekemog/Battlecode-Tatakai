"""Who captures what, and where: camp-capture counts per team up to round R (default 150) in decoded replays.
A capture = a group's reward going from available to taken; the snapshot before names the capturing team.
Per team: captures, gold-cluster captures, captures on our / middle / their third (by group distance to the
two spawn centroids), share of all captures in the game, first capture round, and gold from kills vs camps.
usage: python tools/captures.py MAP DECODED_DIR [R]        top-vs-top games from top-replays/README.md
       python tools/captures.py --file decoded.json TEAM [R]  one local game, TEAM 0 or 1 = our bot"""
import json, os, re, sys, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def analyse(path, upto):
    d = json.load(open(path, encoding='utf-8'))
    R = {}
    for x in d['rounds']:
        if x['phase'] != 12: R[x['round']] = x
    first = R[min(R)]
    cen = {}
    for t in (0, 1):
        ps = [c['position'] for c in first['champions'] if c['team'] == t]
        cen[t] = (sum(p['x'] for p in ps) / len(ps), sum(p['y'] for p in ps) / len(ps))
    gpos = {}
    for c in first['camps']:
        gpos.setdefault(c['group'], []).append(c['position'])
    gmeta = {g: {'n': len(ps), 'cx': sum(p['x'] for p in ps) / len(ps), 'cy': sum(p['y'] for p in ps) / len(ps),
                 'mono': any(c['maxHealth'] >= 20000 for c in first['camps'] if c['group'] == g)} for g, ps in gpos.items()}
    def third(t, g):
        m = gmeta[g]; a = max(abs(m['cx'] - cen[t][0]), abs(m['cy'] - cen[t][1])); e = max(abs(m['cx'] - cen[1 - t][0]), abs(m['cy'] - cen[1 - t][1]))
        f = a / max(1e-9, a + e)
        return 'ours' if f < 1 / 3 else 'theirs' if f > 2 / 3 else 'mid'
    res = {t: {'captures': 0, 'ours': 0, 'mid': 0, 'theirs': 0, 'mono': 0, 'first': None} for t in (0, 1)}
    prev = None
    for r in sorted(R):
        if r > upto: break
        g = R[r]['groups']
        if prev is not None:
            for i, (a, b) in enumerate(zip(prev, g)):
                if a['rewardAvailable'] and not b['rewardAvailable'] and a['captureTeam'] in (0, 1):
                    t = a['captureTeam']; s = res[t]
                    s['captures'] += 1; s[third(t, i)] += 1; s['mono'] += gmeta.get(i, {}).get('mono', False)
                    if s['first'] is None: s['first'] = r
        prev = g
    last = R[max(k for k in R if k <= upto)]
    for t in (0, 1):
        ch = [c for c in last['champions'] if c['team'] == t]
        res[t]['gold'] = sum(c['earnedGold'] for c in ch)
        res[t]['kills'] = sum(c['kda'][0] for c in ch)
        res[t]['kill_gold'] = 50 * res[t]['kills']
    tot = res[0]['captures'] + res[1]['captures']
    for t in (0, 1): res[t]['share'] = res[t]['captures'] / max(1, tot)
    # possible captures: groups x times each could have been taken (respawn cycles) are not modelled; the share is the race result.
    return res

def row(label, s):
    return (f"  {label:22} captures {s['captures']:>3} (ours {s['ours']:>2} / mid {s['mid']:>2} / theirs {s['theirs']:>2})  share {s['share']:.0%}"
            f"  first r{s['first']}  gold {s['gold']:>5.0f}  kills {s['kills']} (={s['kill_gold']} gold)")

def main():
    if sys.argv[1] == '--file':
        path, team = sys.argv[2], int(sys.argv[3]); upto = int(sys.argv[4]) if len(sys.argv) > 4 else 150
        res = analyse(path, upto)
        print(f'{os.path.basename(path)} up to r{upto}'); print(row('our bot', res[team])); print(row('opponent', res[1 - team])); return
    MAP, DEC = sys.argv[1], sys.argv[2]; upto = int(sys.argv[3]) if len(sys.argv) > 3 else 150
    name = lambda s: re.sub(r'\s*\(#\d+\)\s*$', '', s)
    W, L = [], []
    print(f'=== {MAP}: captures up to r{upto}, top-vs-top ===')
    for line in open(os.path.join(ROOT, 'top-replays', 'README.md'), encoding='utf-8'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) != 5 or c[0] != MAP: continue
        p = os.path.join(DEC, c[4].strip('`').replace('.repl26a', '.json'))
        if not os.path.exists(p): continue
        wt = 0 if c[3] == name(c[1]) else 1
        res = analyse(p, upto)
        print(f"{c[4][1:9]}  {c[1]} vs {c[2]} -> {c[3]}")
        print(row('winner', res[wt])); print(row('loser', res[1 - wt]))
        W.append(res[wt]); L.append(res[1 - wt])
    print(f'\n=== {MAP} averages up to r{upto} ===')
    for k in ('captures', 'ours', 'mid', 'theirs', 'share', 'first', 'gold', 'kills'):
        w = [s[k] for s in W if s[k] is not None]; l = [s[k] for s in L if s[k] is not None]
        f = (lambda v: f'{v:.0%}') if k == 'share' else (lambda v: f'{v:.1f}')
        print(f'  {k:9} winners {f(st.mean(w)):>7}   losers {f(st.mean(l)):>7}')

if __name__ == '__main__':
    main()
