"""Match audit: classify every death / lost bag / idle round of OUR champions in decoded ranked
replays and tie each to the bot decision path that produced it. Writes per-match rows and an
aggregate to /home/claude/data/our_rep/audit.json and prints a summary."""
import json, os, glob, collections, sys, re
CYC = sys.argv[sys.argv.index('--cycle') + 1] if '--cycle' in sys.argv else None
sys.argv = [sys.argv[0]]
exec(open('/home/claude/tools/replay/dataset.py').read().split('FEATS =')[0])   # load_map
OUT = '/home/claude/data/our_rep'
idx = json.load(open(f'{OUT}/index.json'))
CH = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi']
CODE = {
    'tribute_channel': 'bank(): started/kept a tribute channel with enemies arriving (unsafe gate / cancel rule)',
    'bank_walk_bag': 'bank(): walking to an altar with a bag (route threat weight / altar choice)',
    'farm_caught': 'handle_enemies(): stayed farming a camp while enemies closed in (evade threshold / favourable calc)',
    'outnumbered_fight': 'handle_enemies(): fought or stayed while outnumbered (favourable = ours >= theirs*need)',
    'enemy_half': 'choose_group()/solo_target(): farming or chasing deep in the enemy half (side penalty / chase rule)',
    'linked_death': 'Cassi & Issac linked death: one of the pair died elsewhere, the other dies with it (protect Cassi; keep Issac near her)',
    'camp_death': 'solo_target()/choose_group(): camp safety check let a champion take a camp that killed it',
    'chase': 'handle_enemies(): chase rule (bag hunting / low-HP target) pulled us into a losing fight',
    'other': 'unclassified',
}
maps = {}
def team_side(side): return 0 if side == 'a' else 1
rows = []; agg = collections.Counter(); bag = collections.Counter(); bymap = collections.defaultdict(collections.Counter)
per_match = []
for js in sorted(glob.glob(f'{OUT}/*.json')):
    mid = os.path.basename(js)[:-5]
    if mid not in idx: continue
    meta = idx[mid]
    if CYC and meta.get('cycle') != CYC: continue
    try: d = json.load(open(js))
    except Exception: continue
    R = d['rounds']
    if len(R) < 60: continue
    name = meta['map']
    if name not in maps:
        try: maps[name] = load_map(name)
        except Exception: continue
    M = maps[name]
    us = team_side(meta['side'])
    sp = M['spawnD']
    if sp is None:
        s2 = [[(c['position']['x'], c['position']['y']) for c in R[1]['champions'] if c['team'] == tm and c.get('position')] for tm in (0, 1)]
        if not s2[0] or not s2[1]: continue
        sp = [M['bfs'](s2[0]), M['bfs'](s2[1])]
    altars = M.get('altars', [])
    # bot logs: slot -> list of (round, action)
    logs = collections.defaultdict(list)
    for f in glob.glob(f'{OUT}/{mid}/team-*.stdout'):
        txt = open(f, 'rb').read().replace(b'\x00', b'').decode('utf8', 'ignore')
        for m in re.finditer(r'P3 r=(\d+) s=(\d+) (\S+) t=(-?\d+)', txt):
            logs[int(m.group(2))].append((int(m.group(1)), m.group(3)))
    ours_idx = [c['entity']['index'] for c in R[20]['champions'] if c['team'] == us]
    slot_of = {e: k for k, e in enumerate(ours_idx)}
    def chpos(c): return (c['position']['x'], c['position']['y']) if c.get('position') else None
    deaths = 0; lost = 0; idle = 0; alive_rounds = 0
    prev = {c['entity']['index']: c for c in R[20]['champions']}
    for t in range(21, len(R)):
        r = R[t]
        cur = {c['entity']['index']: c for c in r['champions']}
        for e in ours_idx:
            c0 = prev.get(e); c1 = cur.get(e)
            if not c0 or not c1: continue
            if c0.get('alive') and not c1.get('alive'):
                deaths += 1
                p = chpos(c0) or (0, 0)
                gems = c0.get('gems') or 0; lost += gems
                en = [o for o in R[t - 1]['champions'] if o['team'] != us and o.get('alive') and chpos(o) and max(abs(chpos(o)[0] - p[0]), abs(chpos(o)[1] - p[1])) <= 5]
                al = [o for o in R[t - 1]['champions'] if o['team'] == us and o['entity']['index'] != e and o.get('alive') and chpos(o) and max(abs(chpos(o)[0] - p[0]), abs(chpos(o)[1] - p[1])) <= 5]
                near_alt = any(max(abs(a[0] - p[0]), abs(a[1] - p[1])) <= 2 for a in altars)
                near_camp = any(min(max(abs(p[0] - x), abs(p[1] - y)) for _, (x, y) in g['camps']) <= 3 for g in M['groups'])
                enemy_half = sp[us][p] > sp[1 - us][p]
                chan = (c0.get('submissionDuration') or 0) > 0 or (c0.get('channelTimer') or 0) > 0
                # bot action logged closest before death for this slot
                k = slot_of.get(e, -1); act = ''
                for rr, a in logs.get(k, []):
                    if rr <= t: act = a
                partner = [o for o in R[t]['champions'] if o['team'] == us and o['entity']['index'] != e and o['type'] in (3, 4) and c0['type'] in (3, 4)]
                linked = any(prev.get(o['entity']['index'], {}).get('alive') and not o.get('alive') for o in partner)
                if linked and not en: cat = 'linked_death'
                elif not en: cat = 'camp_death'
                elif near_alt and (chan or gems > 0): cat = 'tribute_channel'
                elif act == 'chase': cat = 'chase'
                elif len(en) > len(al) + 1: cat = 'outnumbered_fight'
                elif enemy_half: cat = 'enemy_half'
                elif gems >= 40 and not near_camp: cat = 'bank_walk_bag'
                elif near_camp: cat = 'farm_caught'
                else: cat = 'other'
                agg[cat] += 1; bag[cat] += gems; bymap[name][cat] += 1
                rows.append({'match': mid, 'map': name, 'opp': meta['opp'], 'result': meta['result'], 'round': t, 'champ': CH[c0['type']] if c0['type'] < len(CH) else c0['type'],
                             'pos': p, 'gems': gems, 'enemies5': len(en), 'allies5': len(al), 'hp_frac_prev': round((R[t - 3]['champions'][0]['health'] if False else 0), 2),
                             'enemy_half': bool(enemy_half), 'near_altar': near_alt, 'logged_action': act, 'cat': cat})
            if c1.get('alive'): alive_rounds += 1
        prev = cur
    sub = R[-1]['submittedGems']
    per_match.append({'match': mid, 'map': name, 'opp': meta['opp'], 'result': meta['result'], 'v16m': meta['v16m'], 'deaths': deaths,
                      'lost_gems': lost, 'ours': sub[us], 'theirs': sub[1 - us], 'rounds': len(R)})
json.dump({'deaths': rows, 'matches': per_match}, open(f'{OUT}/audit.json', 'w'))
n = len(per_match); nd = sum(agg.values())
print(f'matches analysed {n} (wins {sum(m["result"]=="win" for m in per_match)}), our deaths {nd}, gems lost on death {sum(bag.values())}')
print('deaths by decision path:')
for k, v in agg.most_common():
    print(f'  {v:4} ({v/max(1,nd):.0%})  bags lost {bag[k]:5}  {CODE[k]}')
lw = [m for m in per_match if m['result'] != 'win']
print('losses with <=2 deaths (pure farming races):', sum(1 for m in lw if m['deaths'] <= 2), 'of', len(lw))
print('worst maps by deaths/match:')
mm = collections.defaultdict(list)
for m in per_match: mm[m['map']].append(m['deaths'])
for k, v in sorted(mm.items(), key=lambda kv: -sum(kv[1]) / len(kv[1]))[:8]:
    print(f'  {k:12} {sum(v)/len(v):5.1f} deaths/match  n={len(v)}  top cause: {bymap[k].most_common(1)}')
