"""Deaths of a bot without the Polaris trace (e.g. v50c): per game and per map, by killer, with repeat-death clusters.

usage: deaths50.py BOT DIR [DIR...] [-v]   (games from tools/scan/run_logged.sh: <map>_<first>_<second>.json stats)
A "repeat" is a death of the same champion within 8 tiles of its previous death and within 150 rounds of it
(with respawn ~60 rounds, that is dying again at the same place soon after coming back).
"""
import collections, glob, json, os, re, sys


def main():
    args = [a for a in sys.argv[1:] if a != '-v']
    bot, dirs = args[0], args[1:]
    per_map = collections.defaultdict(lambda: collections.Counter())
    games = []
    for d in dirs:
        for js in sorted(glob.glob(os.path.join(d, '*.json'))):
            tag = os.path.basename(js)[:-5]
            # map names and opponent names may both contain '_': split on our bot's name
            if f'_{bot}_' in tag:
                ours, (mp, opp) = 'A', tag.split(f'_{bot}_', 1)
            else:
                ours, (mp, opp) = 'B', re.match(r'(.*?)_((?:x|h)_[^_]+|[^_]+)$', tag[:-len(bot) - 1]).groups()
            team = 'team' + ours
            s = json.load(open(js))
            win = s['match']['outcome'] == team
            deaths = []
            for e in s['events']:
                if e['kind'] != 'death' or e['owner'].get('team') != team:
                    continue
                for x in e['entries']:
                    deaths.append((x['timestamp']['round'], e['owner']['id'], (x.get('target') or {}).get('kind', '?'), x['x'], x['y']))
            deaths.sort()
            last = {}
            rep = 0
            for r, cid, k, x, y in deaths:
                if cid in last:
                    r0, x0, y0 = last[cid]
                    if r - r0 <= 150 and max(abs(x - x0), abs(y - y0)) <= 8:
                        rep += 1
                last[cid] = (r, x, y)
            kinds = collections.Counter(k for _, _, k, _, _ in deaths)
            games.append((mp, opp, ours, win, len(deaths), kinds['camp'], kinds['champion'], rep, s['match']['roundsStarted']))
            c = per_map[mp]
            c['games'] += 1; c['wins'] += win; c['deaths'] += len(deaths); c['camp'] += kinds['camp']
            c['champ'] += kinds['champion']; c['repeat'] += rep
    n = len(games)
    tot = collections.Counter()
    for c in per_map.values():
        tot.update(c)
    print(f"{bot}: {n} games, wins {tot['wins']}, deaths/game {tot['deaths']/max(1,n):.2f} "
          f"(camp {tot['camp']/max(1,n):.2f}, champion {tot['champ']/max(1,n):.2f}), repeat deaths {tot['repeat']/max(1,n):.2f}/game")
    print(f"{'map':22} games wins  deaths/g  camp/g  champ/g  repeat/g")
    for mp, c in sorted(per_map.items()):
        g = c['games']
        print(f"{mp:22} {g:5} {c['wins']:4}  {c['deaths']/g:8.2f} {c['camp']/g:7.2f} {c['champ']/g:8.2f} {c['repeat']/g:9.2f}")
    if '-v' in sys.argv[1:]:
        for g in sorted(games, key=lambda g: -g[4])[:25]:
            print('  ', g)


if __name__ == '__main__':
    main()
