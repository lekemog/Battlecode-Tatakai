"""Head-to-head summary of BOT vs OPP games from tools/scan/run_logged.sh (both sides of every map).

usage: h2h.py BOT OPP DIR
Prints BOT's wins by side, deaths, submitted gems, gems lost on death and zero-bank games per bot, and the maps where BOT won or lost both sides.
"""
import collections, glob, json, os, sys


def main():
    bot, opp, d = sys.argv[1:4]
    side_w = collections.Counter(); side_n = collections.Counter()
    deaths = collections.Counter(); gems = collections.Counter(); per_map = collections.defaultdict(list)
    lost = collections.Counter(); zero = collections.Counter()
    for js in sorted(glob.glob(os.path.join(d, '*.json'))):
        tag = os.path.basename(js)[:-5]
        if tag.endswith(f'_{bot}_{opp}'):
            mp, ours = tag[:-len(f'_{bot}_{opp}')], 'A'
        elif tag.endswith(f'_{opp}_{bot}'):
            mp, ours = tag[:-len(f'_{opp}_{bot}')], 'B'
        else:
            continue
        s = json.load(open(js))
        me, them = 'team' + ours, 'team' + ('B' if ours == 'A' else 'A')
        win = s['match']['outcome'] == me
        side_w[ours] += win; side_n[ours] += 1
        for e in s['events']:
            if e['kind'] == 'death':
                deaths[bot if e['owner'].get('team') == me else opp] += len(e['entries'])
            if e['kind'] == 'gemLoss':
                lost[bot if e['owner'].get('team') == me else opp] += sum(int(float(x.get('value') or 0)) for x in e['entries'])
        for t in s['teams']:
            gems[bot if t['team'] == me else opp] += int(t['submittedGems'])
            if int(t['submittedGems']) == 0:
                zero[bot if t['team'] == me else opp] += 1
        per_map[mp].append(win)
    n = side_n['A'] + side_n['B']
    print(f"{bot} vs {opp}: {n} games, {bot} wins {side_w['A'] + side_w['B']} "
          f"(as A {side_w['A']}/{side_n['A']}, as B {side_w['B']}/{side_n['B']})")
    print(f"deaths/game {bot} {deaths[bot]/max(1,n):.2f}, {opp} {deaths[opp]/max(1,n):.2f}; "
          f"gems submitted/game {bot} {gems[bot]/max(1,n):.0f}, {opp} {gems[opp]/max(1,n):.0f}")
    print(f"gems lost on death/game {bot} {lost[bot]/max(1,n):.0f}, {opp} {lost[opp]/max(1,n):.0f}; "
          f"games banking 0: {bot} {zero[bot]}, {opp} {zero[opp]}")
    both_w = [m for m, w in per_map.items() if len(w) == 2 and all(w)]
    both_l = [m for m, w in per_map.items() if len(w) == 2 and not any(w)]
    print(f"maps won from both sides ({len(both_w)}): {' '.join(sorted(both_w))}")
    print(f"maps lost from both sides ({len(both_l)}): {' '.join(sorted(both_l))}")


if __name__ == '__main__':
    main()
