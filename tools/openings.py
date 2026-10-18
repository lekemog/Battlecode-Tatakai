"""How top teams open a map: winner vs loser in decoded top-vs-top replays (first ~150 rounds and beyond).
Decode first:  node tools/replay/extract.mjs <visualiser assets> top-replays/<id>.repl26a <dir>/<id>.json
usage: python tools/openings.py MAP DECODED_DIR      (MAP as named in top-replays/README.md, e.g. contest)
Per game and team: draft, first tribute, banked gems at r150/300/600, gold earned and items owned at
r50/100/150, deaths by r150, share of champion-rounds in the middle / enemy third (r0-150), altar locks
used, and the first monolith kill (if any). Zones use each tile's distance to the two spawn centroids."""
import json, os, re, sys, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi']   # as in howtheywin.py
MAP, DEC = sys.argv[1], sys.argv[2]

def index():
    rows = []
    for line in open(os.path.join(ROOT, 'top-replays', 'README.md'), encoding='utf-8'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) == 5 and c[0] == MAP:
            rows.append({'a': c[1], 'b': c[2], 'winner': c[3], 'id': c[4].strip('`').replace('.repl26a', '')})
    return rows

def by_round(d):
    """Last snapshot of each game round (the decoder emits several snapshots per round)."""
    out = {}
    for x in d['rounds']:
        if x['phase'] != 12: out[x['round']] = x   # phase 12 = draft
    return out

def analyse(d, winner_team):
    R = by_round(d); last = max(R)
    first = R[min(R)]
    cen = {}
    for t in (0, 1):
        ps = [c['position'] for c in first['champions'] if c['team'] == t]
        cen[t] = (sum(p['x'] for p in ps) / len(ps), sum(p['y'] for p in ps) / len(ps))
    def zone(t, p):   # 0 = our third, 1 = middle, 2 = enemy third
        dm = max(abs(p['x'] - cen[t][0]), abs(p['y'] - cen[t][1])); de = max(abs(p['x'] - cen[1 - t][0]), abs(p['y'] - cen[1 - t][1]))
        f = dm / max(1e-9, dm + de)
        return 0 if f < 1 / 3 else 2 if f > 2 / 3 else 1
    def snap(r): return R[min(R, key=lambda k: abs(k - r))]
    res = {}
    for t in (0, 1):
        s = {'won': t == winner_team}
        s['draft'] = sorted(CH[c['type']] for c in first['champions'] if c['team'] == t)
        ft = next((r for r in sorted(R) if R[r]['submittedGems'][t] > 0), None)
        s['first_tribute'] = ft               # None = never banked; averaged over teams that did (see never_banked)
        s['never_banked'] = int(ft is None)
        for r in (150, 300, 600): s[f'banked{r}'] = snap(r)['submittedGems'][t] if r <= last else snap(last)['submittedGems'][t]
        for r in (50, 100, 150):
            ch = [c for c in snap(r)['champions'] if c['team'] == t]
            s[f'gold{r}'] = sum(c['earnedGold'] for c in ch)
            # Gold invested = earned - held (review #22: item counts fall when shards merge into an emblem).
            # Tavi's sale refunds are not counted as earned, so this can undercount a selling Tavi.
            s[f'spent{r}'] = sum(c['earnedGold'] - c['gold'] for c in ch)
        s['deaths150'] = sum(c['kda'][1] for c in snap(150)['champions'] if c['team'] == t)
        z = [0, 0, 0]
        for r in range(1, min(150, last) + 1):
            if r not in R: continue
            for c in R[r]['champions']:
                if c['team'] == t and c['alive']: z[zone(t, c['position'])] += 1
        # Thirds by distance to the two spawn centroids. "Enemy third" is stricter than "enemy half" (tools/oppmodel.py).
        tot = max(1, sum(z)); s['mid_share'] = z[1] / tot; s['enemy_third_share'] = z[2] / tot
        res[t] = s
    mono = None
    for r in sorted(R):
        for c in R[r]['camps']:
            if c['type'] == 4 and c['health'] <= 0: mono = r; break
        if mono: break
    return res, mono, last

def main():
    games = []
    for g in index():
        p = os.path.join(DEC, g['id'] + '.json')
        if not os.path.exists(p): print('not decoded:', g['id']); continue
        d = json.load(open(p, encoding='utf-8'))
        name = lambda s: re.sub(r'\s*\(#\d+\)\s*$', '', s)
        wt = 0 if g['winner'] == name(g['a']) else 1 if g['winner'] == name(g['b']) else None
        res, mono, last = analyse(d, wt)
        games.append((g, res, mono, last))
    print(f'=== {MAP}: {len(games)} top-vs-top games ===')
    for g, res, mono, last in games:
        print(f"\n{g['id'][:8]}  {g['a']} vs {g['b']}  -> {g['winner']}  (ended r{last}{', first monolith kill r' + str(mono) if mono else ''})")
        for t in (0, 1):
            s = res[t]
            print(f"  {'WIN ' if s['won'] else 'lose'} {'/'.join(x[:4] for x in s['draft']):34} 1st-trib {str(s['first_tribute']):>4}  banked150/300/600 {s['banked150']:>4}/{s['banked300']:>4}/{s['banked600']:>4}"
                  f"  gold50/100/150 {s['gold50']:>4}/{s['gold100']:>4}/{s['gold150']:>4}  spent100 {s['spent100']:>4}  deaths150 {s['deaths150']}"
                  f"  mid-third {s['mid_share']:.0%} enemy-third {s['enemy_third_share']:.0%}")
    keys = ['never_banked', 'first_tribute', 'banked150', 'banked300', 'banked600', 'gold50', 'gold100', 'gold150',
            'spent50', 'spent100', 'spent150', 'deaths150', 'mid_share', 'enemy_third_share']
    print(f"\n=== {MAP} averages: winners vs losers ===")
    for k in keys:
        w = [res[t][k] for _, res, _, _ in games for t in (0, 1) if res[t]['won'] and res[t][k] is not None]
        l = [res[t][k] for _, res, _, _ in games for t in (0, 1) if not res[t]['won'] and res[t][k] is not None]
        if w and l:
            f = (lambda v: f'{v:.0%}') if 'share' in k or k == 'never_banked' else (lambda v: f'{v:.1f}')
            print(f'  {k:14} winners {f(st.mean(w)):>7}   losers {f(st.mean(l)):>7}')
    from collections import Counter
    print('  winners picked:', Counter(x for _, res, _, _ in games for t in (0, 1) if res[t]['won'] for x in res[t]['draft']).most_common())
    print('  losers picked: ', Counter(x for _, res, _, _ in games for t in (0, 1) if not res[t]['won'] for x in res[t]['draft']).most_common())

if __name__ == '__main__':
    main()
