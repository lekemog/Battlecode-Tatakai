"""opening5.py DECODED.json [...] : opening shape of both teams from engine-3 decoded replays (tools/replay/extract5.mjs).

Per team, rounds 1..R (default 150): main-group size (largest single-link cluster of alive champions off spawn, link 6),
share of champions in it, numbers advantage when an enemy champion is within reach (6): rounds where the team has more /
fewer champions within 6 of the contact than the enemy, first champion death round, deaths by R, stun rounds suffered.
Prints one row per team per game and the mean per team label (draft-agnostic).
Usage: python3 -I opening5.py [--r 150] [--names A,B] files...
"""
import json
import sys


def cheb(a, b):
    return max(abs(a['x'] - b['x']), abs(a['y'] - b['y']))


def clusters(pts, link=6):
    n = len(pts); seen = [False] * n; out = []
    for i in range(n):
        if seen[i]:
            continue
        stack = [i]; seen[i] = True; c = 0
        while stack:
            j = stack.pop(); c += 1
            for k in range(n):
                if not seen[k] and cheb(pts[j], pts[k]) <= link:
                    seen[k] = True; stack.append(k)
        out.append(c)
    return out


def analyse(path, R):
    d = json.load(open(path))
    rows = {0: dict(main=0.0, share=0.0, n=0, ahead=0, behind=0, even=0, deaths=0, first=None, stunned=0),
            1: dict(main=0.0, share=0.0, n=0, ahead=0, behind=0, even=0, deaths=0, first=None, stunned=0)}
    prev_alive = {}
    spawn = {}
    for st in d['rounds']:
        r = st['round']
        if st.get('phase') != 1 or r < 1:
            continue
        if r > R:
            break
        ch = st['champions']
        for c in ch:
            key = (c['team'], c['entity']['index'])
            if key not in spawn:
                spawn[key] = c['position']
            if prev_alive.get(key) and not c['alive']:
                t = rows[c['team']]; t['deaths'] += 1
                if t['first'] is None:
                    t['first'] = r
            prev_alive[key] = c['alive']
            if c['alive'] and any(b.get('type') in (1, 'stun') or 'stun' in json.dumps(b).lower() for b in c.get('buffs', [])):
                rows[c['team']]['stunned'] += 1
        for team in (0, 1):
            act = [c['position'] for c in ch if c['team'] == team and c['alive'] and cheb(c['position'], spawn[(team, c['entity']['index'])]) > 4]
            if len(act) >= 1:
                cl = clusters(act); t = rows[team]
                t['main'] += max(cl); t['share'] += max(cl) / len(act); t['n'] += 1
            ours = [c['position'] for c in ch if c['team'] == team and c['alive']]
            theirs = [c['position'] for c in ch if c['team'] != team and c['alive']]
            # contact rounds: some pair within 6; compare counts near the contact centre (our champion in contact)
            best = None
            for p in ours:
                if any(cheb(p, q) <= 6 for q in theirs):
                    a = sum(1 for q in ours if cheb(p, q) <= 6)
                    e = sum(1 for q in theirs if cheb(p, q) <= 6)
                    if best is None or a - e < best:
                        best = a - e
            if best is not None:
                t = rows[team]
                if best > 0: t['ahead'] += 1
                elif best < 0: t['behind'] += 1
                else: t['even'] += 1
    return d, rows


def main():
    args = sys.argv[1:]; R = 150; names = None
    if args[:1] == ['--r']:
        R = int(args[1]); args = args[2:]
    if args[:1] == ['--names']:
        names = args[1].split(','); args = args[2:]
    agg = {}
    for f in args:
        try:
            d, rows = analyse(f, R)
        except Exception as e:
            print('skip', f, e); continue
        for team in (0, 1):
            t = rows[team]; n = max(1, t['n'])
            label = names[team] if names else f'team{team}'
            print(f"{f.split('/')[-1][:40]:40s} {label:12s} main {t['main']/n:4.2f} share {t['share']/n:4.2f} "
                  f"contact ahead/even/behind {t['ahead']:3d}/{t['even']:3d}/{t['behind']:3d} deaths<=r{R} {t['deaths']} first {t['first']} buff1 {t['stunned']}")
            a = agg.setdefault(label, [0, 0.0, 0.0, 0, 0, 0, 0, 0])
            a[0] += 1; a[1] += t['main'] / n; a[2] += t['share'] / n; a[3] += t['ahead']; a[4] += t['even']; a[5] += t['behind']; a[6] += t['deaths']; a[7] += t['stunned']
    for k, a in agg.items():
        g = a[0]
        print(f"MEAN {k:12s} games {g} main {a[1]/g:.2f} share {a[2]/g:.2f} ahead {a[3]/g:.1f} even {a[4]/g:.1f} behind {a[5]/g:.1f} deaths {a[6]/g:.2f} buff1 {a[7]/g:.1f} (buff type 1, unverified as stun)")


if __name__ == '__main__':
    main()
