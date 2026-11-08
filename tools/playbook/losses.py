"""losses.py SUMDIR LIST_LOST LIST_WON ME.json : why we lose, from match summaries (`cambc matches summary --json`).

Per game, for our side and theirs: final gems, deaths, kills, first death round, deaths before r300, gems lost on death
(gemLoss events), gems banked by r400, earned gold at r300 (championTimelines), rounds played, first bank round.
Prints win/loss means and classifies each loss:
  fights   : our deaths >= theirs + 3;
  bank     : we lost >= 300 gems on death, or banked nothing before r400;
  economy  : earned gold at r300 behind by >= 15% (and not the above);
  close    : lost by < 150 gems at the end (and not the above);
  other.
"""
import collections
import json
import os
import sys


def series_at(tl, r):
    s = []
    for run in tl['runs']:
        s += [float(run['value'])] * int(run['duration'])
    return s[min(r, len(s) - 1)] if s else 0.0


def side_stats(d, side):
    other = 'teamB' if side == 'teamA' else 'teamA'
    out = {}
    for t, key in ((side, 'us'), (other, 'them')):
        champs = [c for c in d['champions'] if c['team'] == t]
        out[key + '_deaths'] = sum(int(c['metrics']['deaths']) for c in champs)
        out[key + '_kills'] = sum(int(c['metrics']['kills']) for c in champs)
        out[key + '_gems'] = int([x for x in d['teams'] if x['team'] == t][0]['submittedGems'])
        out[key + '_gold300'] = sum(series_at(tl, 300) for tl in d['championTimelines'] if tl['metric'] == 'earnedGold' and tl['owner'].get('team') == t)
        out[key + '_gold600'] = sum(series_at(tl, 600) for tl in d['championTimelines'] if tl['metric'] == 'earnedGold' and tl['owner'].get('team') == t)
        out[key + '_banked400'] = sum(series_at(tl, 400) for tl in d['championTimelines'] if tl['metric'] == 'submittedGems' and tl['owner'].get('team') == t)
    deaths = collections.defaultdict(list); lost = collections.Counter(); first_bank = {}
    for e in d['events']:
        own = e.get('owner', {})
        t = own.get('team')
        for en in e.get('entries', []):
            r = en['timestamp']['round']
            if e['kind'] == 'death':
                deaths[t].append(r)
            elif e['kind'] == 'gemLoss':
                lost[t] += float(en.get('amount') or en.get('value') or 0)
            elif e['kind'] == 'gemSubmission':
                first_bank[t] = min(first_bank.get(t, 99999), r)
    for t, key in ((side, 'us'), (other, 'them')):
        ds = sorted(deaths[t])
        out[key + '_first_death'] = ds[0] if ds else 2000
        out[key + '_deaths300'] = sum(1 for r in ds if r < 300)
        out[key + '_gemloss'] = lost[t]
        out[key + '_first_bank'] = first_bank.get(t, 2000)
    out['rounds'] = int(d['match'].get('roundsCompleted', 0))
    return out


def load(listf, sumdir):
    rows = []
    for line in open(listf):
        p = line.split()
        if len(p) < 4:
            continue
        mid, opp, side, mp = p[0], p[1], p[2], p[3]
        f = os.path.join(sumdir, mid + '.json')
        if not os.path.exists(f):
            continue
        d = json.load(open(f))
        s = side_stats(d, 'teamA' if side == 'a' else 'teamB')
        s.update(mid=mid, opp=opp, map=mp)
        rows.append(s)
    return rows


def main():
    sumdir, lostf, wonf = sys.argv[1:4]
    L, W = load(lostf, sumdir), load(wonf, sumdir)
    keys = ['deaths', 'kills', 'deaths300', 'first_death', 'gemloss', 'banked400', 'first_bank', 'gold300', 'gold600', 'gems']
    print(f'losses {len(L)}  wins {len(W)}')
    print(f'   {"metric":12s} {"loss us/them":>20s} {"win us/them":>20s}')
    for k in keys:
        f = lambda R, s: sum(r[s + '_' + k] for r in R) / max(1, len(R))
        print(f'   {k:12s} {f(L, "us"):9.1f} /{f(L, "them"):8.1f}  {f(W, "us"):9.1f} /{f(W, "them"):8.1f}')
    print(f'   rounds       loss {sum(r["rounds"] for r in L) / len(L):.0f}  win {sum(r["rounds"] for r in W) / len(W):.0f}')
    cat = collections.Counter(); ex = collections.defaultdict(list)
    for r in L:
        if r['us_deaths'] >= r['them_deaths'] + 3:
            c = 'fights'
        elif r['us_gemloss'] >= 300 or r['us_banked400'] == 0:
            c = 'bank'
        elif r['us_gold300'] < 0.85 * r['them_gold300']:
            c = 'economy'
        elif r['them_gems'] - r['us_gems'] < 150:
            c = 'close'
        else:
            c = 'other'
        cat[c] += 1; ex[c].append(f"{r['map']} vs {r['opp']} ({r['us_gems']}-{r['them_gems']}, deaths {r['us_deaths']}-{r['them_deaths']}, lost {r['us_gemloss']:.0f}, gold300 {r['us_gold300']:.0f}/{r['them_gold300']:.0f})")
    print('loss causes:', dict(cat))
    for c, v in ex.items():
        print(f'  {c}:')
        for x in v[:6]:
            print('     ', x)


if __name__ == '__main__':
    main()
