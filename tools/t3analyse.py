"""T3 (#40) analysis of decoded ranked games (from tools/t3fetch.py): us vs the opponent per map.
usage: python tools/t3analyse.py DIR MAP [UPTO=600]
Per team, up to round 150 and UPTO:
  captures by third (own / middle / enemy), gold earned
  deaths, split by cause: 'champion' if an enemy champion's kill count rose that round, else 'camp/other';
         and by what the champion was doing in its last 3 alive rounds: 'retreating' (distance to own spawn
         centroid fell by >=2) or 'recall' (channelType != 0 on its last alive round) vs 'other'
  idle: share of alive champion-rounds off spawn (>3 tiles from own spawn centroid) with no position change
  longest still streak: champion, rounds, position, nearest camp distance and whether that camp group's reward
         was available, gems carried, and the distance to the nearest altar
Caveat: 'retreating' is a geometric proxy (moving towards home), not the bot's own decision label."""
import json, os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from captures import analyse as captures

CH = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi']
DIR, MAP = sys.argv[1], sys.argv[2]; UPTO = int(sys.argv[3]) if len(sys.argv) > 3 else 600
cheb = lambda p, q: max(abs(p['x'] - q[0]), abs(p['y'] - q[1]))
chname = lambda t: CH[t] if 0 <= t < len(CH) else f'type{t}'   # the patch added champion types beyond the original 12

def by_round(d):
    R = {}
    for x in d['rounds']:
        if x['phase'] != 12: R[x['round']] = x
    return R

def team_metrics(d, t):
    R = by_round(d); rs = sorted(R); first = R[rs[0]]
    cen = {}
    for s in (0, 1):
        ps = [c['position'] for c in first['champions'] if c['team'] == s]
        cen[s] = (sum(p['x'] for p in ps) / len(ps), sum(p['y'] for p in ps) / len(ps))
    altars = None
    out = {'deaths': 0, 'by_champ': 0, 'by_camp': 0, 'retreating': 0, 'recall': 0, 'deaths150': 0}
    hist = {}; idle = alive_off = 0; streak = {}; best = None
    prev = None; prev_camp_hp = {}
    for r in rs:
        if r > UPTO: break
        x = R[r]
        if prev is not None:
            kills_up = sum(c['kda'][0] for c in x['champions'] if c['team'] != t) > sum(c['kda'][0] for c in prev['champions'] if c['team'] != t)
            pc = {(c['entity']['index']): c for c in prev['champions']}
            for c in x['champions']:
                if c['team'] != t: continue
                k = c['entity']['index']; p = pc.get(k)
                if p and p['alive'] and not c['alive']:
                    out['deaths'] += 1; out['deaths150'] += r <= 150
                    out['by_champ' if kills_up else 'by_camp'] += 1
                    h = hist.get(k, [])
                    if p.get('channelType'): out['recall'] += 1
                    elif len(h) >= 3 and h[-3] - h[-1] >= 2: out['retreating'] += 1
        for c in x['champions']:
            if c['team'] != t: continue
            k = c['entity']['index']
            if not c['alive']: hist[k] = []; streak[k] = None; continue
            dh = cheb(c['position'], cen[t]); hist.setdefault(k, []).append(dh); hist[k] = hist[k][-4:]
            if dh > 3:
                alive_off += 1
                pk = next((pc2 for pc2 in prev['champions'] if pc2['entity']['index'] == k), None) if prev is not None else None
                # Idle = did not move, lost no health, and no camp within 4 tiles lost health (standing still while
                # hitting a camp is not idle).
                same = bool(pk) and pk['alive'] and pk['position'] == c['position'] and pk['health'] <= c['health'] \
                    and not any(cheb(cm['position'], (c['position']['x'], c['position']['y'])) <= 4 and cm.get('health', 0) < prev_camp_hp.get(cm['entity']['index'], cm.get('health', 0))
                                for cm in x['camps'] if 'position' in cm)
                idle += same
                s = streak.get(k)
                if same:
                    s = s or {'start': r - 1, 'pos': c['position']}; s['len'] = r - s['start']; streak[k] = s
                    if best is None or s['len'] > best['len']:
                        best = dict(s, champ=chname(c['type']), gems=c['gems'], end=r, hp=c['health'])
                else: streak[k] = None
            else: streak[k] = None
        prev = x
        prev_camp_hp = {cm['entity']['index']: cm.get('health', 0) for cm in x['camps']}
    out['idle_share'] = idle / max(1, alive_off)
    if best:
        x = R[best['end']]
        camps = [(cheb(c['position'], (best['pos']['x'], best['pos']['y'])), c) for c in x['camps'] if c.get('health', 0) > 0 and 'position' in c]
        if camps:
            dist, cmp = min(camps, key=lambda z: z[0])
            g = x['groups'][cmp['group']] if cmp['group'] < len(x['groups']) else {}
            best['nearest_live_camp'] = dist; best['camp_awake'] = cmp.get('awake'); best['camp_group_state'] = g.get('state')
        rew = [i for i, g in enumerate(x['groups']) if g.get('rewardAvailable')]
        best['rewards_available'] = len(rew)
    out['longest_still'] = best
    return out

def main():
    idx = [r for r in json.load(open(os.path.join(DIR, 'index.json'))) if r['map'] == MAP and r['decoded']]
    rows = []
    for g in idx:
        p = os.path.join(DIR, g['id'] + '.json')
        d = json.load(open(p, encoding='utf-8')); t = g['team']
        c150 = captures(p, 150); cU = captures(p, UPTO)
        us, them = team_metrics(d, t), team_metrics(d, 1 - t)
        rows.append((g, c150, cU, us, them))
        b = us['longest_still']
        print(f"{g['id'][:8]} {g['result']:4} vs {g['opponent'][:22]:22} | caps r150 {c150[t]['captures']:>2} (o{c150[t]['ours']}/m{c150[t]['mid']}/e{c150[t]['theirs']}) vs {c150[1-t]['captures']:>2} (m{c150[1-t]['mid']})"
              f" | gold150 {c150[t]['gold']:>5.0f} vs {c150[1-t]['gold']:>5.0f} | deaths r{UPTO} {us['deaths']:>2} (champ {us['by_champ']}, camp {us['by_camp']}; retreat {us['retreating']}, recall {us['recall']}) vs {them['deaths']:>2}"
              f" | idle {us['idle_share']:.0%} vs {them['idle_share']:.0%}"
              + (f" | still {b['len']}r {b['champ']} r{b['start']}-{b['end']} at ({b['pos']['x']},{b['pos']['y']}) gems {b['gems']} camp@{b.get('nearest_live_camp')} rewards {b.get('rewards_available')}" if b else ''))
    if not rows: print('no decoded games'); return
    m = lambda f: st.mean(f(r) for r in rows)
    t = lambda r: r[0]['team']
    print(f"\n=== {MAP}: {len(rows)} decoded ranked games, {sum(r[0]['result'] == 'win' for r in rows)} wins ===")
    print(f"captures r150      us {m(lambda r: r[1][t(r)]['captures']):.1f} (own {m(lambda r: r[1][t(r)]['ours']):.1f} / mid {m(lambda r: r[1][t(r)]['mid']):.1f} / enemy {m(lambda r: r[1][t(r)]['theirs']):.1f})"
          f"   them {m(lambda r: r[1][1-t(r)]['captures']):.1f} (own {m(lambda r: r[1][1-t(r)]['ours']):.1f} / mid {m(lambda r: r[1][1-t(r)]['mid']):.1f} / enemy {m(lambda r: r[1][1-t(r)]['theirs']):.1f})")
    print(f"captures r{UPTO}      us {m(lambda r: r[2][t(r)]['captures']):.1f} (mid {m(lambda r: r[2][t(r)]['mid']):.1f})   them {m(lambda r: r[2][1-t(r)]['captures']):.1f} (mid {m(lambda r: r[2][1-t(r)]['mid']):.1f})")
    print(f"gold r150          us {m(lambda r: r[1][t(r)]['gold']):.0f}   them {m(lambda r: r[1][1-t(r)]['gold']):.0f}")
    print(f"gold r{UPTO}          us {m(lambda r: r[2][t(r)]['gold']):.0f}   them {m(lambda r: r[2][1-t(r)]['gold']):.0f}")
    print(f"deaths to r{UPTO}     us {m(lambda r: r[3]['deaths']):.1f} (by champion {m(lambda r: r[3]['by_champ']):.1f}, camp/other {m(lambda r: r[3]['by_camp']):.1f};"
          f" retreating {m(lambda r: r[3]['retreating']):.1f}, recalling {m(lambda r: r[3]['recall']):.1f})   them {m(lambda r: r[4]['deaths']):.1f} (retreating {m(lambda r: r[4]['retreating']):.1f})")
    print(f"deaths to r150     us {m(lambda r: r[3]['deaths150']):.1f}   them {m(lambda r: r[4]['deaths150']):.1f}")
    print(f"idle share         us {m(lambda r: r[3]['idle_share']):.0%}   them {m(lambda r: r[4]['idle_share']):.0%}")
    ls = sorted([r for r in rows if r[3]['longest_still']], key=lambda r: -r[3]['longest_still']['len'])[:5]
    print('longest still streaks (ours):', ', '.join(f"{r[0]['id'][:8]} {r[3]['longest_still']['len']}r {r[3]['longest_still']['champ']}" for r in ls))

if __name__ == '__main__':
    main()
