"""fishstudy.py [TEAM_ID] [SINCE] [MAX] -> download and decode a team's finished ranked matches; cache compact per-game metrics.
Default team: ladder #1 Intercontinental Fish; default since: patch 3.0 (2026-10-20T10:05Z). Cache: data/fish_cache.json.
Per game, for the studied side (S) and the opponent (O): draft (champion types), gems, gold timeline, deaths, kills, camp kills by
type, monolith kills, first bank round, bank count and bag sizes, item sets at r400/r800 per champion, map-half occupancy,
team spread (mean pairwise distance), HP fraction when dying, deaths caused by camps, recalls (jumps to spawn)."""
import json, os, sys, subprocess, zipfile, tempfile, shutil, collections, statistics as st
TEAM = sys.argv[1] if len(sys.argv) > 1 else '1890540d-1ffc-4847-adbf-d0d08772f268'
SINCE = sys.argv[2] if len(sys.argv) > 2 else '2026-10-20T10:05'
MAX = int(sys.argv[3]) if len(sys.argv) > 3 else 400
D = '/home/claude/data/fish'; os.makedirs(D, exist_ok=True)
CACHE = f'/home/claude/data/fish_cache_{TEAM[:8]}.json'
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def listing():
    cur = None; out = []
    for _ in range(30):
        a = ['cambc', 'matches', 'list', '--team', TEAM, '--kind', 'ranked', '--limit', '100', '--json'] + (['--cursor', cur] if cur else [])
        try: d = json.loads(subprocess.run(a, capture_output=True, text=True, timeout=120).stdout)
        except Exception: break
        for x in d['matches']:
            if x['status'] == 'finished' and x['createdAt'] >= SINCE: out.append(x)
        cur = d.get('nextCursor')
        if not cur or (d['matches'] and min(x['createdAt'] for x in d['matches']) < SINCE): break
    return out

def cheb(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
def P(c): p = c.get('position'); return (p['x'], p['y']) if p else None

def analyse(R, s):
    o = 1 - s; T = len(R) - 1; out = {}
    gold = lambda t, w: sum(c.get('earnedGold', 0) for c in R[min(t, T)]['champions'] if c['team'] == w)
    out['rounds'] = T
    out['gems'] = [R[T]['submittedGems'][s], R[T]['submittedGems'][o]]
    out['gold'] = {str(t): [gold(t, s), gold(t, o)] for t in (100, 200, 400, 800, 1200, T)}
    out['gold']['end'] = out['gold'].pop(str(T))
    out['draft'] = [[c.get('type') for c in R[min(30, T)]['champions'] if c['team'] == w] for w in (s, o)]
    spawn = {}
    for c in R[min(25, T)]['champions']:
        if P(c): spawn.setdefault(c['team'], []).append(P(c))
    sc = {w: (st.mean(p[0] for p in v), st.mean(p[1] for p in v)) for w, v in spawn.items()}
    dead = [0, 0]; camp_dead = [0, 0]; hp_at_death = [[], []]; kills = collections.Counter(); first_bank = [None, None]
    banks = [[], []]; recalls = [0, 0]; half = [0, 0]; half_n = [0, 0]; spread = []
    pa = {}; ph = {}; pg = {}
    for t in range(5, T + 1):
        rr = R[t]; pr = R[t - 1]
        prevc = {c['entity']['index']: c for c in pr['champions']}
        for c in rr['champions']:
            i = c['entity']['index']; w = 0 if c['team'] == s else 1; p0 = prevc.get(i)
            if p0 and p0.get('alive') and not c.get('alive'):
                dead[w] += 1
                if p0.get('maxHealth'): hp_at_death[w].append(p0['health'] / p0['maxHealth'])
                pp = P(p0)
                if pp:
                    en = any(h['team'] != c['team'] and h.get('alive') and P(h) and cheb(P(h), pp) <= 5 for h in pr['champions'])
                    cm = any(m['health'] > 0 and m.get('awake') and P(m) and cheb(P(m), pp) <= 5 for m in pr['camps'])
                    if cm and not en: camp_dead[w] += 1
            if p0 and c.get('alive') and p0.get('alive'):
                g0 = p0.get('gems') or 0; g1 = c.get('gems') or 0
                if g1 < g0 and c.get('alive'): banks[w].append(g0)
                a, b = P(p0), P(c)
                if a and b and cheb(a, b) >= 4 and c['team'] in sc and cheb(b, sc[c['team']]) <= 4: recalls[w] += 1
            if c.get('alive') and P(c) and len(sc) == 2:
                own = sc[c['team']]; en = sc[1 - c['team']]
                half_n[w] += 1; half[w] += cheb(P(c), en) < cheb(P(c), own)
        for w, team in ((0, s), (1, o)):
            if first_bank[w] is None and rr['submittedGems'][team] > 0: first_bank[w] = t
        if t % 25 == 0:
            ps = [P(c) for c in rr['champions'] if c['team'] == s and c.get('alive') and P(c)]
            if len(ps) >= 2: spread.append(st.mean(cheb(a, b) for k, a in enumerate(ps) for b in ps[k + 1:]))
        pc = {c['entity']['index']: c for c in pr['camps']}
        for c in rr['camps']:
            p0 = pc.get(c['entity']['index'])
            if p0 and p0['health'] > 0 and c['health'] <= 0 and P(p0):
                al = [h for h in rr['champions'] if h.get('alive') and P(h)]
                if al:
                    b = min(al, key=lambda h: cheb(P(h), P(p0)))
                    kills[(0 if b['team'] == s else 1, p0['type'])] += 1
    out['deaths'] = dead; out['camp_deaths'] = camp_dead
    out['hp_at_death'] = [round(st.mean(x), 3) if x else None for x in hp_at_death]
    out['camp_kills'] = {f'{w}_{k}': v for (w, k), v in kills.items()}
    out['first_bank'] = first_bank; out['banks'] = [len(b) for b in banks]
    out['bag_median'] = [st.median(b) if b else 0 for b in banks]
    out['recalls'] = recalls
    out['enemy_half'] = [round(half[w] / half_n[w], 3) if half_n[w] else None for w in (0, 1)]
    out['spread'] = round(st.mean(spread), 2) if spread else None
    def items(t):
        res = []
        for c in R[min(t, T)]['champions']:
            if c['team'] == s: res.append([c.get('type'), {k: x for k, x in enumerate(c.get('items') or []) if x}])
        return res
    out['items400'] = items(400); out['items800'] = items(800)
    out['maxhp400'] = [[c.get('type'), c.get('maxHealth')] for c in R[min(400, T)]['champions'] if c['team'] == s]
    return out

if __name__ == '__main__':
    M = listing()[:MAX]
    print('matches listed', len(M), flush=True)
    n = 0
    for x in M:
        mid = x['matchId']
        if mid in cache: continue
        me = [t for t in x['teams'] if t.get('teamId') == TEAM]
        if not me: continue
        me = me[0]; opp = [t for t in x['teams'] if t is not me][0]
        z = f'{D}/{mid}.zip'
        if not os.path.exists(z): subprocess.run(['cambc', 'matches', 'download', mid, '-o', z], capture_output=True, timeout=300)
        tmp = tempfile.mkdtemp(dir=D)
        try:
            zipfile.ZipFile(z).extractall(tmp)
            rp = [os.path.join(a, f) for a, _, fs in os.walk(tmp) for f in fs if f.endswith('.repl26a')][0]
            subprocess.run(['node', '/home/claude/tools/replay/extract3.mjs', '/home/claude/data/vis3/assets', rp, f'{tmp}/r.json'], capture_output=True, timeout=600)
            R = json.load(open(f'{tmp}/r.json'))['rounds']
            s = 0 if me.get('side') == 'a' else 1
            rec = analyse(R, s)
            rec.update(map=x['map'], result=me.get('result'), opp=opp.get('name'), at=x['createdAt'], side=me.get('side'))
            cache[mid] = rec; n += 1
        except Exception as e:
            print('skip', mid[:8], type(e).__name__, flush=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        if n % 10 == 0: json.dump(cache, open(CACHE, 'w'))
    json.dump(cache, open(CACHE, 'w'))
    print('cached', len(cache), 'new', n)
