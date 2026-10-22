"""Respawn-blocking mechanism check (#40 T3): for decoded games, measure how often our champions block camp groups
whose respawn is due (timer at 0, no live camps) by standing on their spawn tiles.
usage: python tools/spawnblock.py DECODED_JSON TEAM [DECODED_JSON TEAM ...]
Per game, for TEAM (0 = side A, 1 = side B), non-monolith groups only:
  due_blocked   rounds where a group is due to respawn but one of TEAM's alive champions stands on its spawn tiles
  worst_block   longest such stretch (group, rounds)
  delays        for every respawn: rounds from the timer reaching 0 to camps reappearing (0 = on time); max and total
  stuck_10      stretches of >=10 rounds with the same TEAM champion on a due group's spawn tile (for a fixed bot this
                would mean the step-off to the ring failed, e.g. ring occupied or unreachable)
Monolith groups are excluded: blocking them is deliberate (boss_battle)."""
import json, sys, collections

def analyse(path, team):
    d = json.load(open(path, encoding='utf-8'))
    R = {}
    for x in d['rounds']:
        if x['phase'] != 12: R[x['round']] = x
    rs = sorted(R); f = R[rs[0]]
    spawns = collections.defaultdict(set); mono = set()
    for c in f['camps']:
        if 'position' in c: spawns[c['group']].add((c['position']['x'], c['position']['y']))
        if c.get('maxHealth', 0) >= 20000: mono.add(c['group'])
    due_since = {}; delays = []; due_blocked = 0; worst = (0, None); cur = {}; stuck = []; on_tile = {}
    for r in rs:
        x = R[r]
        live = collections.Counter(c['group'] for c in x['camps'] if c.get('health', 0) > 0)
        ours = [(c['entity']['index'], (c['position']['x'], c['position']['y'])) for c in x['champions'] if c['team'] == team and c['alive']]
        for gi, g in enumerate(x['groups']):
            if gi in mono or gi not in spawns: continue
            due = live[gi] == 0 and g.get('state') == 3 and g.get('respawnRounds', -1) == 0
            if due and gi not in due_since: due_since[gi] = r
            if live[gi] > 0 and gi in due_since: delays.append(r - due_since.pop(gi))
            blockers = [k for k, p in ours if p in spawns[gi]]
            if due and blockers:
                due_blocked += 1; cur[gi] = cur.get(gi, 0) + 1
                if cur[gi] > worst[0]: worst = (cur[gi], gi)
            else: cur[gi] = 0
            for k in blockers if due else []:
                s = on_tile.get((k, gi))
                on_tile[(k, gi)] = (s[0], r) if s and s[1] == r - 1 else (r, r)
        for key, (a, b) in list(on_tile.items()):
            if b < r:   # stretch ended
                if b - a + 1 >= 10: stuck.append((key[0], key[1], a, b))
                del on_tile[key]
    for key, (a, b) in on_tile.items():
        if b - a + 1 >= 10: stuck.append((key[0], key[1], a, b))
    return {'due_blocked': due_blocked, 'worst_block': worst, 'max_delay': max(delays) if delays else 0,
            'total_delay': sum(delays), 'respawns': len(delays), 'stuck_10': stuck, 'rounds': rs[-1]}

def main():
    a = sys.argv[1:]
    for path, team in zip(a[::2], a[1::2]):
        m = analyse(path, int(team))
        print(f"{path.replace(chr(92), '/').split('/')[-1]:40} team {team}: due_blocked {m['due_blocked']:>4} | worst {m['worst_block'][0]:>4}r (group {m['worst_block'][1]})"
              f" | respawns {m['respawns']:>3}, max delay {m['max_delay']:>4}, total delay {m['total_delay']:>5} | stuck>=10r: {len(m['stuck_10'])}")

if __name__ == '__main__':
    main()
