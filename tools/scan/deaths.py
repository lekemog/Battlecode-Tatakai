"""Classify every death of our bot by what it was doing just before: the last trace decision of that champion.

usage: deaths.py BOT DIR [DIR...]   (games from tools/scan/run_logged.sh: <tag>.repl26a bundles + <tag>.json stats)
Trace slot k is our team's k-th champion in roster (id) order. For each death this prints counts by killer (camp or
champion), by the last logged action within 15 rounds before it, and by HP at that decision, for wins and losses.
"""
import collections, glob, json, os, re, sys, zipfile

TRACE = re.compile(r'T (\d+) (\d) ([a-z-]+) (-?\d+) (-?\d+) (\d+) (\d+) (\d+) (\d+)')


def main():
    bot, dirs = sys.argv[1], sys.argv[2:]
    by_action = collections.Counter(); by_hp = collections.Counter(); by_gems = collections.Counter()
    near_enemy = collections.Counter(); games = 0; n = collections.Counter(); examples = collections.defaultdict(list)
    for d in dirs:
        for js in sorted(glob.glob(os.path.join(d, '*.json'))):
            tag = os.path.basename(js)[:-5]
            bundle = os.path.join(d, tag + '.repl26a')
            if not os.path.exists(bundle):
                continue
            ours = 'a' if '_'.join(tag.split('_')[1:]).startswith(bot + '_') else 'b'
            team = 'team' + ours.upper()
            stats = json.load(open(js))
            lost = stats['match']['outcome'] != team
            ids = sorted(c['id'] for c in stats['roster']['champions'] if c['team'] == team)
            slot_of = {cid: k for k, cid in enumerate(ids)}
            maxhp = {}
            raw = zipfile.ZipFile(bundle).read(f'team-{ours}.stdout').decode('utf-8', 'replace')
            rows = collections.defaultdict(list)
            for m in TRACE.finditer(raw):
                r, s, a, t, hp, gems, ne, e6, a5 = m.groups()
                rows[int(s)].append((int(r), a, int(t), int(hp), int(gems), int(ne), int(e6)))
                maxhp[int(s)] = max(maxhp.get(int(s), 0), int(hp))
            for v in rows.values():
                v.sort()
            games += 1
            for e in stats['events']:
                if e['kind'] != 'death' or e['owner'].get('team') != team:
                    continue
                slot = slot_of.get(e['owner']['id'])
                for x in e['entries']:
                    rd = x['timestamp']['round']
                    killer = (x.get('target') or {}).get('kind', '?')
                    prev = [row for row in rows.get(slot, []) if rd - 15 <= row[0] <= rd]
                    if not prev:
                        key = (killer, 'no-trace')
                        by_action[key] += 1; n[killer] += 1
                        continue
                    last = prev[-1]
                    frac = last[3] / max(1, maxhp.get(slot, 1))
                    hpb = '<30%' if frac < .3 else '30-60%' if frac < .6 else '>60%'
                    by_action[(killer, last[1])] += 1
                    by_hp[(killer, hpb)] += 1
                    by_gems[(killer, 'bag' if last[4] > 0 else 'no bag')] += 1
                    near_enemy[(killer, 'enemy<=6' if last[5] <= 6 else 'no enemy near')] += 1
                    n[killer] += 1
                    if len(examples[(killer, last[1])]) < 3:
                        examples[(killer, last[1])].append(f'{tag} r{rd} slot {slot} ({x["x"]},{x["y"]}) hp {last[3]}')
    print(f'{bot}: {games} games; deaths to camps {n["camp"]} ({n["camp"]/max(1,games):.2f}/game), '
          f'to champions {n["champion"]} ({n["champion"]/max(1,games):.2f}/game)')
    for killer in ('camp', 'champion'):
        tot = max(1, n[killer])
        print(f'\n== killed by {killer}: last decision before death')
        for (k, a), c in by_action.most_common():
            if k == killer and c / tot >= .02:
                print(f'  {a:14} {c:5}  {100*c/tot:5.1f}%   e.g. {examples[(k, a)][:1]}')
        print('  HP at that decision: ' + ', '.join(f'{h} {100*c/tot:.0f}%' for (k, h), c in sorted(by_hp.items()) if k == killer))
        print('  carrying: ' + ', '.join(f'{h} {100*c/tot:.0f}%' for (k, h), c in sorted(by_gems.items()) if k == killer))
        print('  enemies: ' + ', '.join(f'{h} {100*c/tot:.0f}%' for (k, h), c in sorted(near_enemy.items()) if k == killer))


if __name__ == '__main__':
    main()
