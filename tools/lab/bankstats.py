"""bankstats.py BOT DIR [DIR ...]: banking habit of BOT in local game stats (mirror.sh output folders).

Per folder: games, wins, mean banked / collected gems, games with 0 banked, deaths and gems not converted
(collected - banked - still carried at the end, i.e. mostly lost on death). Use it to judge banking changes
(the top-ten zero-bank finding, results/zero-bank-2026-11): a candidate should bank more, lose less and keep wins.
"""
import glob
import json
import os
import sys


def team_of(path, bot):
    base = os.path.basename(path)[:-5]
    m, rest = base.split('_', 1)
    return m, ('teamA' if rest.startswith(bot + '_') else 'teamB')


def main():
    bot = sys.argv[1]
    for d in sys.argv[2:]:
        n = w = zero = 0
        banked = collected = deaths = lost = 0.0
        for f in sorted(glob.glob(os.path.join(d, '*.json'))):
            if f.endswith('manifest.json'):
                continue
            try:
                j = json.load(open(f))
            except Exception:
                continue
            m, side = team_of(f, bot)
            mine = [c for c in j['champions'] if c['team'] == side]
            sub = sum(int(c['metrics']['submittedGems']) for c in mine)
            col = sum(int(c['metrics']['collectedGems']) for c in mine)
            held = sum(int(c['metrics']['gems']) for c in mine)
            n += 1
            w += j['match']['outcome'] == side
            zero += sub == 0
            banked += sub
            collected += col
            lost += max(0, col - sub - held)
            deaths += sum(int(c['metrics']['deaths']) for c in mine)
        if n == 0:
            print(f'{d}: no games')
            continue
        print(f'{os.path.basename(d.rstrip("/"))}: games {n} wins {w} ({w / n:.1%})  banked {banked / n:.0f}  collected {collected / n:.0f}'
              f'  zero-bank {zero}  deaths {deaths / n:.1f}  unconverted {lost / n:.0f}')


if __name__ == '__main__':
    main()
