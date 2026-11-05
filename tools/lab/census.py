"""census.py PANEL_LABEL [PANEL_LABEL ...] : top-team style census (wards, capture recipients, tribute size, gold concentration,
early kills, gem loss) for us vs the opponents in real games, from results/panel/<label>.json and results/panel/summaries/<match>.json.

The metrics follow the definitions of a public top-20 census (1,040 ranked games) so the numbers can be compared line by line:
single-recipient capture = share of group captures where one champion of the team got the reward; carry share = largest champion share of
team earned gold; tribute = one gemSubmission event; gem loss = (collected - submitted - still held) / collected.
"""
import collections
import glob
import json
import os
import statistics
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'panel')


def team_stats(j, team):
    ch = [c for c in j['champions'] if c['team'] == team]
    ev = [e for e in j['events'] if e['owner'].get('team') == team]
    m = lambda c, k: float(c['metrics'][k])
    gold = [m(c, 'earnedGold') for c in ch]
    sub = sum(m(c, 'submittedGems') for c in ch)
    col = sum(m(c, 'collectedGems') for c in ch)
    held = sum(m(c, 'gems') for c in ch)
    wards = sum(len(e['entries']) for e in ev if e['kind'] == 'wardPlacement')
    kills_early = sum(1 for e in ev if e['kind'] == 'kill' for x in e['entries'] if x['timestamp']['round'] < 200)
    trib = [float(x['value']) for e in ev if e['kind'] == 'gemSubmission' for x in e['entries'] if float(x['value']) > 0]
    first_trib = min([x['timestamp']['round'] for e in ev if e['kind'] == 'gemSubmission' for x in e['entries']] or [None], key=lambda v: 1e9 if v is None else v)
    # captures: a group clear event per champion; count champions sharing the same group within 6 rounds
    clears = []
    for e in ev:
        if e['kind'] == 'campClear':
            for x in e['entries']:
                clears.append((x['target']['id'], x['timestamp']['round'], e['owner']['id']))
    clears.sort()
    groups = []
    for g, r, o in clears:
        if groups and groups[-1]['g'] == g and r - groups[-1]['r'] <= 6:
            groups[-1]['owners'].add(o)
        else:
            groups.append({'g': g, 'r': r, 'owners': {o}})
    single = sum(1 for g in groups if len(g['owners']) == 1)
    return {
        'wards': wards, 'captures': len(groups), 'single_share': single / len(groups) if groups else None,
        'carry_share': max(gold) / sum(gold) if sum(gold) else None, 'gold': sum(gold),
        'tributes': len(trib), 'tribute_mean': statistics.mean(trib) if trib else None, 'first_tribute': first_trib,
        'submitted': sub, 'collected': col, 'loss_share': max(0.0, col - sub - held) / col if col else None,
        'deaths': sum(m(c, 'deaths') for c in ch), 'kills': sum(m(c, 'kills') for c in ch), 'early_kills': kills_early,
    }


def main():
    rows = {'us': [], 'them': []}
    for label in sys.argv[1:]:
        p = json.load(open(os.path.join(ROOT, label + '.json')))
        for opp, games in p['games'].items():
            for g in games:
                f = os.path.join(ROOT, 'summaries', g['match'] + '.json')
                if not os.path.exists(f):
                    continue
                j = json.load(open(f))
                mine = 'teamA' if g['side'] == 'a' else 'teamB'
                theirs = 'teamB' if mine == 'teamA' else 'teamA'
                rows['us'].append(team_stats(j, mine))
                rows['them'].append(team_stats(j, theirs))
    n = len(rows['us'])
    print(f'{n} games from {", ".join(sys.argv[1:])}\n')
    print(f'{"metric":28s} {"us":>9s} {"them":>9s}')
    def avg(side, k):
        v = [r[k] for r in rows[side] if r[k] is not None]
        return statistics.mean(v) if v else float('nan')
    def med(side, k):
        v = [r[k] for r in rows[side] if r[k] is not None]
        return statistics.median(v) if v else float('nan')
    for name, k, f, fmt in (
        ('wards placed / game', 'wards', avg, '%9.1f'), ('group captures / game', 'captures', avg, '%9.1f'),
        ('single-recipient captures', 'single_share', avg, '%9.2f'), ('carry gold share (max champ)', 'carry_share', avg, '%9.2f'),
        ('earned gold / game', 'gold', avg, '%9.0f'), ('tributes / game', 'tributes', avg, '%9.1f'),
        ('mean tribute size (gems)', 'tribute_mean', avg, '%9.1f'), ('first tribute round (median)', 'first_tribute', med, '%9.0f'),
        ('gems submitted / game', 'submitted', avg, '%9.0f'), ('gems collected / game', 'collected', avg, '%9.0f'),
        ('gem loss share', 'loss_share', avg, '%9.2f'), ('deaths / game', 'deaths', avg, '%9.1f'),
        ('kills / game', 'kills', avg, '%9.1f'), ('kills before round 200', 'early_kills', avg, '%9.2f')):
        print(f'{name:28s} {fmt % f("us", k)} {fmt % f("them", k)}')


if __name__ == '__main__':
    main()
