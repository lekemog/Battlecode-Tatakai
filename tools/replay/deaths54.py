"""#54: label every death of our team in a decoded replay (tools/replay/extract4.mjs) from its last rounds.

usage: python3 -I tools/replay/deaths54.py <decoded.json> <our_team_index 0|1> [summary.json]
Per death: round, champion, tile, distance to our spawn, health 10/5/2 rounds before, enemy champions and allies within 6
tiles one round before, awake camps within their range, bag carried, item points owned (ours vs the killer's team average),
and a label: outnumbered (enemy champions > allies incl. self within 6), duel (equal numbers), camp (no enemy champion
near, awake camp in range), burst (>=70% health 3 rounds before and dead), lone-chase (no ally within 6).
Positions are end-of-round snapshots."""
import json, sys, collections
cheb = lambda a, b: max(abs(a[0] - b[0]), abs(a[1] - b[1]))
def pos(c): return (c['position']['x'], c['position']['y'])
def main(path, us, summary=None):
    d = json.load(open(path)); R = d['rounds']
    by = {r['round']: r for r in R}
    out = []
    spawn_c = None
    first = R[min(3, len(R) - 1)]
    mine0 = [pos(c) for c in first['champions'] if c['team'] == us and 'position' in c]
    spawn_c = (sum(p[0] for p in mine0) // max(1, len(mine0)), sum(p[1] for p in mine0) // max(1, len(mine0))) if mine0 else (0, 0)
    prev_alive = {}
    for r in R:
        rd = r['round']
        for c in r['champions']:
            if c['team'] != us: continue
            i = c['entity']['index']
            if prev_alive.get(i, True) and not c['alive']:
                p0 = by.get(rd - 1, r)
                cc = next(x for x in p0['champions'] if x['entity']['index'] == i and x['team'] == us)
                if 'position' not in cc: prev_alive[i] = c['alive']; continue
                here = pos(cc)
                def hp(k):
                    q = by.get(rd - k)
                    if not q: return None
                    z = next((x for x in q['champions'] if x['entity']['index'] == i and x['team'] == us), None)
                    return int(z['health']) if z and z['alive'] else 0
                en = [x for x in p0['champions'] if x['team'] != us and x['alive'] and 'position' in x and cheb(pos(x), here) <= 6]
                al = [x for x in p0['champions'] if x['team'] == us and x['alive'] and 'position' in x and x['entity']['index'] != i and cheb(pos(x), here) <= 6]
                cm = [k for k in p0['camps'] if k.get('awake') and k['health'] > 0 and 'position' in k and cheb(pos(k), here) <= k['attackRange'] + 1]
                items_us = sum(sum(x['items']) for x in p0['champions'] if x['team'] == us)
                items_en = sum(sum(x['items']) for x in p0['champions'] if x['team'] != us)
                h3 = hp(3)
                if len(en) > len(al) + 1: lab = 'outnumbered'
                elif len(en) >= 1 and len(en) >= len(al) + 1: lab = 'duel/outnumbered-1'
                elif en: lab = 'duel-with-help'
                elif cm: lab = 'camp'
                else: lab = 'unseen'
                tags = [lab]
                if h3 is not None and h3 >= 0.7 * cc['maxHealth']: tags.append('burst')
                if not al: tags.append('lone')
                if cc['gems'] > 0: tags.append('bag%d' % cc['gems'])
                out.append(dict(round=rd, champ=cc['type'], at=here, home=cheb(here, spawn_c), hp10=hp(10), hp5=hp(5), hp2=hp(2), enemies=[(x['type'], cheb(pos(x), here)) for x in en], allies=len(al), camps=len(cm), items=(items_us, items_en), tags=tags))
            prev_alive[i] = c['alive']
    return out
if __name__ == '__main__':
    o = main(sys.argv[1], int(sys.argv[2]))
    for x in o: print(x)
    c = collections.Counter(x['tags'][0] for x in o); print(dict(c), 'lone', sum('lone' in x['tags'] for x in o), 'burst', sum('burst' in x['tags'] for x in o), 'deaths', len(o))
