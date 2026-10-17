"""Per-team feature rows from extracted replay JSON. usage: analyze.py <json_dir> -> <json_dir>/teams.json"""
import json, glob, os, sys, math, collections

CH = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi', 'HeartOfRuin']
ITEMS = ('Monster Shard of Strength.Monster Emblem of Strength.Monster Shard of Focus.Monster Emblem of Focus.Monster Shard of Health.Monster Emblem of Health.'
         'Power Shard of Strength.Power Emblem of Strength.Power Shard of Focus.Power Emblem of Focus.Power Shard of Health.Power Emblem of Health.'
         'Durability Shard of Strength.Durability Emblem of Strength.Durability Shard of Focus.Durability Emblem of Focus.Durability Shard of Health.Durability Emblem of Health.'
         'Treasure Shard of Strength.Treasure Emblem of Strength.Treasure Shard of Focus.Treasure Emblem of Focus.Treasure Shard of Health.Treasure Emblem of Health.'
         'Jungle Shard of Strength.Jungle Emblem of Strength.Jungle Shard of Focus.Jungle Emblem of Focus.Jungle Shard of Health.Jungle Emblem of Health.'
         'Home Shard of Strength.Home Emblem of Strength.Home Shard of Focus.Home Emblem of Focus.Home Shard of Health.Home Emblem of Health.'
         'Bruiser Shard of Strength.Bruiser Emblem of Strength.Bruiser Shard of Focus.Bruiser Emblem of Focus.Bruiser Shard of Health.Bruiser Emblem of Health').split('.')
K_RECALL, K_SUBMIT, K_SHOP, K_WARD, K_CONS, K_GEMS, K_LOCK, K_TP, K_SELL = 11, 12, 13, 14, 15, 18, 20, 21, 25


def short(name):
    w = name.split()
    return w[0] + ('E' if w[1] == 'Emblem' else 's') + '-' + w[3][0]


def analyze(path, mapname):
    d = json.load(open(path))
    R = d['rounds']
    last = R[-1]
    h = last['_h']
    champs = last['champions']
    team_of = {c['entity']['index']: c['team'] for c in champs}
    type_of = {c['entity']['index']: CH[c['type']] for c in champs}
    out = {}
    for t in (0, 1):
        f = dict(map=mapname, match=os.path.basename(path)[6:14], team=t, rounds=h['round'],
                 win=(h['outcome'] == t + 1), gems=h['submittedGems'][t], opp_gems=h['submittedGems'][1 - t])
        f['comp'] = sorted(type_of[i] for i in team_of if team_of[i] == t)
        mine = [c for c in champs if c['team'] == t]
        f['kills'] = sum(c['kda'][0] for c in mine)
        f['deaths'] = sum(c['kda'][1] for c in mine)
        f['earned_gold'] = sum(c['earnedGold'] for c in mine)
        out[t] = f

    # Event counts and first rounds
    ev = collections.defaultdict(lambda: collections.Counter())
    first = collections.defaultdict(dict)
    seen = set()
    for e in d['events']:
        rnd, kind, ak, ai = e[0], e[1], e[2], e[3]
        if ak != 1 or ai not in team_of: continue
        key = (rnd, kind, ai, e[6], e[7])
        if key in seen: continue
        seen.add(key)
        t = team_of[ai]
        ev[t][kind] += 1
        first[t].setdefault(kind, rnd)

    # Submitted gems timeline and tribute sizes
    gems_at = {0: {}, 1: {}}
    prev = [0, 0]
    tributes = {0: [], 1: []}
    for r in R:
        rnd = r['_h']['round']; sg = r['_h']['submittedGems']
        for t in (0, 1):
            if sg[t] > prev[t]: tributes[t].append((rnd, sg[t] - prev[t]))
            gems_at[t][rnd] = sg[t]
        prev = list(sg)

    def at(t, rr):
        ks = [k for k in gems_at[t] if k <= rr]
        return gems_at[t][max(ks)] if ks else 0

    # Captures: group goes to state 3, credited to captureTeam the round before
    caps = {0: 0, 1: 0, 2: 0}
    caps100 = {0: 0, 1: 0, 2: 0}
    prevg = None
    for r in R:
        g = r['groups']
        if prevg and len(prevg) == len(g):
            for a, b in zip(prevg, g):
                if a['state'] == 2 and b['state'] == 3:
                    caps[a['captureTeam']] += 1
                    if r['_h']['round'] <= 150: caps100[a['captureTeam']] += 1
        prevg = g

    # Item purchase order (first 6 distinct buys per team) and first buy round
    buys = {0: [], 1: []}
    previt = {}
    for r in R:
        rnd = r['_h']['round']
        for c in r['champions']:
            i = c['entity']['index']; it = c.get('items')
            if it is None: continue
            if i in previt:
                for k, (a, b) in enumerate(zip(previt[i], it)):
                    if b > a: buys[team_of[i]].append((rnd, type_of[i], short(ITEMS[k])))
            previt[i] = it

    # Spread: mean pairwise distance between alive champions, rounds 30-200
    spread = {0: [], 1: []}
    solo = {0: [], 1: []}
    for r in R:
        rnd = r['_h']['round']
        if not 30 <= rnd <= 200: continue
        for t in (0, 1):
            ps = [(c['position']['x'], c['position']['y']) for c in r['champions'] if c['team'] == t and c.get('alive') and c.get('position')]
            if len(ps) < 2: continue
            ds = [math.dist(a, b) for i, a in enumerate(ps) for b in ps[i + 1:]]
            spread[t].append(sum(ds) / len(ds))
            # groups: champions within 5 tiles are linked
            n = len(ps); par = list(range(n))
            def fd(x):
                while par[x] != x: x = par[x]
                return x
            for i in range(n):
                for j in range(i + 1, n):
                    if math.dist(ps[i], ps[j]) <= 5: par[fd(i)] = fd(j)
            solo[t].append(len({fd(i) for i in range(n)}))

    for t in (0, 1):
        f = out[t]
        f['captures'] = caps[t]; f['captures_r150'] = caps100[t]
        f['g100'] = at(t, 100); f['g200'] = at(t, 200); f['g300'] = at(t, 300); f['g400'] = at(t, 400)
        f['first_tribute'] = tributes[t][0][0] if tributes[t] else None
        f['n_tributes'] = len(tributes[t])
        f['avg_tribute'] = round(sum(x for _, x in tributes[t]) / len(tributes[t]), 1) if tributes[t] else 0
        f['first_buy'] = buys[t][0][0] if buys[t] else None
        f['buys'] = buys[t][:8]
        f['n_buys'] = len(buys[t])
        f['wards'] = ev[t][K_WARD]; f['recalls'] = ev[t][K_RECALL]; f['locks'] = ev[t][K_LOCK]
        f['teleports'] = ev[t][K_TP]; f['consumables'] = ev[t][K_CONS]; f['sells'] = ev[t][K_SELL]
        f['first_ward'] = first[t].get(K_WARD); f['first_recall'] = first[t].get(K_RECALL)
        f['spread'] = round(sum(spread[t]) / len(spread[t]), 1) if spread[t] else None
        f['groups'] = round(sum(solo[t]) / len(solo[t]), 2) if solo[t] else None
    return [out[0], out[1]]


if __name__ == '__main__':
    J = sys.argv[1]
    maps = json.load(open(os.path.join(J, 'maps.json')))
    rows = []
    for p in sorted(glob.glob(os.path.join(J, 'match-*.json'))):
        mid = os.path.basename(p)[:-5]
        rows += analyze(p, maps[mid][0])
    json.dump(rows, open(os.path.join(J, 'teams.json'), 'w'), indent=1)
    for f in rows:
        print(f"{f['map']:11} {f['match']} T{f['team']} {'W' if f['win'] else 'L'} {f['gems']:5}-{f['opp_gems']:<5} r{f['rounds']:<5}"
              f" K{f['kills']:<3}D{f['deaths']:<3} cap{f['captures']:<3}({f['captures_r150']:<2}) g200={f['g200']:<4} 1stTrib={f['first_tribute']} "
              f"trib={f['n_tributes']}x{f['avg_tribute']} 1stBuy={f['first_buy']} wards={f['wards']} rec={f['recalls']} locks={f['locks']} tp={f['teleports']}"
              f" spread={f['spread']} grp={f['groups']} {','.join(f['comp'])}")
