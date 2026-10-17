"""Per-team feature rows from match summaries. usage: feat.py  -> writes /home/claude/data/feat.json"""
import json, os, glob, collections

def tl_at(runs, R):
    s = 0; v = 0
    for r in runs:
        if s > R: break
        v = float(r['value']); s += r['duration']
    return v

def first_reach(runs, g):
    s = 0
    for r in runs:
        if float(r['value']) >= g: return s
        s += r['duration']
    return None

def rows_for(path, mapname, label_of_team):
    d = json.load(open(path))
    m = d['match']; win = m['outcome']; R = m['roundsStarted']
    names = {c['id']: c for c in d['roster']['champions']}
    out = []
    for team in ('teamA', 'teamB'):
        lab = label_of_team(team)
        if lab is None: continue
        f = dict(label=lab, map=mapname, win=(team == win), rounds=R, file=os.path.basename(path))
        f['gems'] = [int(t['submittedGems']) for t in d['teams'] if t['team'] == team][0]
        f['opp_gems'] = [int(t['submittedGems']) for t in d['teams'] if t['team'] != team][0]
        tt = [t for t in d['teamTimelines'] if t['owner'] == team][0]['runs']
        f['g200'] = tl_at(tt, 200); f['g400'] = tl_at(tt, 400)
        f['first_score'] = first_reach(tt, 1)
        champs = [c for c in d['champions'] if c['team'] == team]
        f['n'] = len(champs)
        f['deaths'] = sum(float(c['metrics']['deaths']) for c in champs)
        f['kills'] = sum(float(c['metrics']['kills']) for c in champs)
        f['gold'] = sum(float(c['metrics']['earnedGold']) for c in champs)
        col = sorted((float(c['metrics']['collectedGems']) for c in champs), reverse=True)
        f['top_share'] = col[0] / max(1, sum(col))
        f['champ_dmg'] = sum(float(c['metrics']['championDamageDone']) for c in champs)
        f['mon_dmg'] = sum(float(c['metrics']['monsterDamageDone']) for c in champs)
        ev = collections.defaultdict(list)
        for e in d['events']:
            o = e['owner']
            if o.get('team') == team or (o.get('kind') == 'team' and o.get('name') == team):
                ev[e['kind']] += e['entries']
        # gold timeline per team at 100/200
        gt = [t for t in d['championTimelines'] if t['metric'] == 'earnedGold' and t['owner'].get('team') == team]
        f['gold100'] = sum(tl_at(t['runs'], 100) for t in gt); f['gold200'] = sum(tl_at(t['runs'], 200) for t in gt)
        subs = [int(x['value']) for x in ev['gemSubmission'] if int(x['value']) > 0]
        f['n_sub'] = len(subs); f['avg_sub'] = sum(subs) / len(subs) if subs else 0
        f['camp_clears'] = len(ev['campClear'])
        f['big_camps'] = sum(1 for x in ev['gemCollection'] if int(x['value']) >= 30 and x['context'] == 'campGroup')
        f['gems_from_kills'] = sum(int(x['value']) for x in ev['gemCollection'] if x['context'] != 'campGroup')
        f['wards'] = len(ev['wardPlacement'])
        cons = collections.Counter(x['target']['name'] for x in ev['buyConsumable'])
        f['locks'] = cons.get('Altar Lock', 0); f['tps'] = cons.get('Teleport Crystal', 0)
        buys = sorted(ev['buyItem'], key=lambda x: x['timestamp']['round'])
        f['first_buy'] = buys[0]['timestamp']['round'] if buys else None
        emb = sorted(ev['itemCombination'], key=lambda x: x['timestamp']['round'])
        f['emblems'] = [x['target']['name'] for x in emb]
        f['first_emblems'] = {}
        firsts = {}
        for x in emb:
            # owner per entry not available here; take global order
            pass
        kr = [x['timestamp']['round'] for x in ev['kill']]
        f['kills_early'] = sum(1 for r in kr if r < 200)
        f['lost_gems'] = sum(int(x['value']) for x in ev['gemLoss'])
        out.append(f)
    return out

def main():
    rows = []
    top = json.load(open('/home/claude/data/top/top.json'))
    TM = json.load(open('/home/claude/data/top/topmatches.json'))
    for p in glob.glob('/home/claude/data/top/sum/*.json'):
        mid = os.path.basename(p)[:-5]; m = TM.get(mid)
        if not m: continue
        side = {('team' + t['side'].upper()): t for t in m['teams']}
        try:
            rows += rows_for(p, m['map'], lambda team: f"top{top[side[team]['teamId']]}" if team in side else None)
        except Exception as e:
            pass
    ours = {m['matchId']: m for m in json.load(open('/home/claude/data/rk100.json'))['matches']}
    for mid, m in ours.items():
        p = f'/home/claude/data/ranked2/{mid}.json'
        if not os.path.exists(p): continue
        us = [t for t in m['teams'] if t['teamId'].startswith('9c16')][0]
        ourside = 'team' + us['side'].upper()
        try:
            rows += rows_for(p, m['map'], lambda team: 'US' if team == ourside else 'OPP')
        except Exception as e:
            pass
    json.dump(rows, open('/home/claude/data/feat.json', 'w'))
    print(len(rows))

main()
