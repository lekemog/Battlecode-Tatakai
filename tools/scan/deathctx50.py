"""Context of each death of one team in a decoded replay (tools/replay/extract4.mjs output) plus its statistics JSON.

usage: deathctx50.py REPLAY_JSON STATS_JSON TEAM(A|B)
For each death: round, champion, max HP, distance to its own spawn, rounds since it last (re)spawned, enemies and
allies within 5 tiles the round before, and the summed max HP of those enemies vs those allies (level gap proxy).
"""
import json, sys

NAMES = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi', 'HoR']


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def main():
    rj, sj, side = sys.argv[1], sys.argv[2], sys.argv[3]
    R = json.load(open(rj))['rounds']
    S = json.load(open(sj))
    team = 'team' + side
    ti = 0 if side == 'A' else 1
    pos = lambda c: (c['position']['x'], c['position']['y']) if c.get('position') else None
    by_round = {r['_h']['round']: r for r in R}
    spawn = [pos(c) for c in R[min(5, len(R) - 1)]['champions'] if c['team'] == ti and pos(c)]
    sc = (sum(p[0] for p in spawn) / len(spawn), sum(p[1] for p in spawn) / len(spawn))
    ids = sorted(c['id'] for c in S['roster']['champions'] if c['team'] == team)
    # roster id -> entity index: champions are listed team A first in both, in id order
    deaths = []
    for e in S['events']:
        if e['kind'] != 'death' or e['owner'].get('team') != team:
            continue
        for x in e['entries']:
            deaths.append((x['timestamp']['round'], e['owner']['id'], e['owner'].get('name', '?'), (x.get('target') or {}).get('kind', '?'), (x['x'], x['y'])))
    deaths.sort()
    alive_since = {}
    prev_death = {}
    rows = []
    for rd, cid, name, killer, p in deaths:
        r = by_round.get(rd - 1)
        if not r:
            continue
        me = next((c for c in r['champions'] if c['entity']['index'] == cid), None)
        en = [c for c in r['champions'] if c['team'] != ti and c.get('alive') and pos(c) and cheb(pos(c), p) <= 5]
        al = [c for c in r['champions'] if c['team'] == ti and c.get('alive') and pos(c) and c['entity']['index'] != cid and cheb(pos(c), p) <= 5]
        since = rd - prev_death.get(cid, 0)
        prev_death[cid] = rd
        rows.append((rd, name[:10], killer, int(me['maxHealth']) if me else -1, round(cheb(p, sc)), since, len(en), len(al),
                     int(sum(c['maxHealth'] for c in en)), int(sum(c['maxHealth'] for c in al) + (me['maxHealth'] if me else 0))))
    print('round champ      killer   maxhp spawnD sinceLast enemies5 allies5 enemyMaxHP ourMaxHP')
    for row in rows:
        print('%5d %-10s %-8s %5d %6d %9d %8d %7d %10d %8d' % row)
    if rows:
        n = len(rows)
        print(f'{n} deaths; median spawn distance {sorted(r[4] for r in rows)[n // 2]}; '
              f'alone (no ally within 5) {sum(r[7] == 0 for r in rows)}; outnumbered {sum(r[6] > r[7] + 1 for r in rows)}; '
              f'died within 100 rounds of previous death {sum(r[5] <= 100 for r in rows)}')
    fin = R[-1]
    print('final max HP ours', [int(c['maxHealth']) for c in fin['champions'] if c['team'] == ti],
          'theirs', [int(c['maxHealth']) for c in fin['champions'] if c['team'] != ti])


if __name__ == '__main__':
    main()
