"""fishreport.py CACHE [CACHE2] -> aggregate report of a studied team's ranked games (from fishstudy.py); optional second cache to compare."""
import json, sys, collections, statistics as st
NAMES = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi', 'HeartOfRuin']
ITEM_GROUP = ['Monster', 'Power', 'Durability', 'Treasure', 'Jungle', 'Home', 'Bruiser']
ITEM_KIND = ['Str shard', 'Str emblem', 'Foc shard', 'Foc emblem', 'HP shard', 'HP emblem']
def iname(k): return f'{ITEM_GROUP[k // 6]} {ITEM_KIND[k % 6]}' if k < 42 else str(k)
def mean(xs): xs = [x for x in xs if x is not None]; return st.mean(xs) if xs else float('nan')
def load(p): return list(json.load(open(p)).values())

def summary(G, label):
    W = [g for g in G if g['result'] == 'win']
    print(f'\n=== {label}: {len(G)} games, {len(W)} wins ({100 * len(W) / max(1, len(G)):.0f}%)')
    f = lambda key, i: mean([g[key][i] for g in G])
    print(f"  deaths {f('deaths',0):.1f} vs opp {f('deaths',1):.1f} | camp-only deaths {f('camp_deaths',0):.1f} vs {f('camp_deaths',1):.1f} | HP when dying {f('hp_at_death',0):.2f}")
    for t in ('100', '200', '400', '800', 'end'):
        print(f"  gold @{t:>4}: {mean([g['gold'].get(t,g['gold']['end'])[0] for g in G]):7.0f} vs {mean([g['gold'].get(t,g['gold']['end'])[1] for g in G]):7.0f}")
    print(f"  first bank round median {st.median([g['first_bank'][0] or 2000 for g in G]):.0f} vs {st.median([g['first_bank'][1] or 2000 for g in G]):.0f} | banks/game {f('banks',0):.1f} vs {f('banks',1):.1f} | median bag {f('bag_median',0):.0f} vs {f('bag_median',1):.0f}")
    print(f"  recalls/game {f('recalls',0):.1f} vs {f('recalls',1):.1f} | time on enemy half {100*f('enemy_half',0):.0f}% vs {100*f('enemy_half',1):.0f}% | team spread {mean([g['spread'] for g in G]):.1f} tiles | rounds {mean([g['rounds'] for g in G]):.0f}")
    ck = collections.Counter(); co = collections.Counter()
    for g in G:
        for k, v in g['camp_kills'].items():
            w, t = k.split('_'); (ck if w == '0' else co)[int(t)] += v
    tn = ['wolf', 'elk', 'gem cl', 'gold cl', 'monolith', 'golem']
    print('  camp kills/game: ' + ', '.join(f'{tn[t]} {ck[t]/len(G):.1f} vs {co[t]/len(G):.1f}' for t in sorted(set(ck) | set(co))))

def drafts(G):
    print('\n--- Drafts (champion sets) by pick count, with win rate')
    by = collections.defaultdict(collections.Counter); wins = collections.defaultdict(collections.Counter)
    for g in G:
        d = tuple(sorted(NAMES[x] for x in g['draft'][0] if x is not None))
        by[len(d)][d] += 1; wins[len(d)][d] += g['result'] == 'win'
    for n in sorted(by):
        print(f'  {n} bodies:')
        for d, c in by[n].most_common(5): print(f'    {c:3}x {wins[n][d]:3}W  {", ".join(d)}')
    pk = collections.Counter()
    for g in G:
        for x in g['draft'][0]: pk[NAMES[x]] += 1
    print('  champion frequency:', ', '.join(f'{k} {v}' for k, v in pk.most_common()))

def items(G):
    print('\n--- Items at r800 per champion (share of games owning each item) and max HP at r400')
    own = collections.defaultdict(collections.Counter); n = collections.Counter(); hp = collections.defaultdict(list)
    for g in G:
        for t, it in g['items800']:
            if t is None: continue
            n[t] += 1
            for k in it: own[t][int(k)] += 1
        for t, h in g['maxhp400']:
            if t is not None and h: hp[t].append(h)
    for t in sorted(n, key=lambda t: -n[t]):
        top = ', '.join(f'{iname(k)} {100 * v / n[t]:.0f}%' for k, v in own[t].most_common(7))
        print(f'  {NAMES[t]:11} (n={n[t]:3}, maxHP@400 {mean(hp[t]):.0f}): {top}')

def maps(G):
    print('\n--- By map: games, win%, deaths vs opp, gold@400 vs opp, first bank, enemy-half%')
    by = collections.defaultdict(list)
    for g in G: by[g['map']].append(g)
    for m, gs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        w = sum(g['result'] == 'win' for g in gs)
        print(f"  {m:24} {len(gs):3} {100*w/len(gs):4.0f}%  deaths {mean([g['deaths'][0] for g in gs]):5.1f}/{mean([g['deaths'][1] for g in gs]):5.1f}  gold400 {mean([g['gold'].get('400',g['gold']['end'])[0] for g in gs]):5.0f}/{mean([g['gold'].get('400',g['gold']['end'])[1] for g in gs]):5.0f}  bank r{st.median([g['first_bank'][0] or 2000 for g in gs]):.0f}  enemy-half {100*mean([g['enemy_half'][0] for g in gs]):.0f}%  mono {mean([g['camp_kills'].get('0_4',0) for g in gs]):.1f}")

def losses(G):
    L = [g for g in G if g['result'] != 'win']
    print(f'\n--- Losses ({len(L)}): opponent, map')
    for g in L: print(f"  {g['opp']:24} {g['map']:22} gems {g['gems'][0]}-{g['gems'][1]} deaths {g['deaths'][0]}-{g['deaths'][1]}")

if __name__ == '__main__':
    A = load(sys.argv[1]); summary(A, 'Studied team'); drafts(A); items(A); maps(A); losses(A)
    if len(sys.argv) > 2: B = load(sys.argv[2]); summary(B, 'Comparison team'); drafts(B); items(B); maps(B)
