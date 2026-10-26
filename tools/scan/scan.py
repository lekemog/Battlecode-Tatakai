"""Pathology scanner: finds behaviour bugs in our bot's decision traces across many games.

usage: scan.py BOT DIR [DIR...]
  DIR holds games from `cambc run-batch` with replay bundles kept: <tag>.repl26a (zip with team-a/b.stdout) and
  <tag>.json (statistics, --json). Tags are MAP_FIRST_SECOND, as bench/bench.py writes them; BOT names our side.
  Our bot must print v18t-style trace lines: "T round slot action target hp gems nearest e6 a5 flags agg ratio".

Each game is checked for five problems, each measured in champion-rounds lost:
  flipflop  - two actions alternating every 1-2 rounds (6+ switches in a row), e.g. capture <-> pvp-engage
  deadend   - 150+ champion-rounds on a camp-group target our team never clears that game
  idle      - single spans of 25+ rounds in a waiting action (stand, stage, idle, *-wait)
  hotspot   - 3+ of our deaths within 4 tiles of each other (the trace action before each death is listed)
  bag       - gems carried 150+ rounds without a tribute
Output: the problems ranked by total champion-rounds (losses count double), with example games.
"""
import collections, glob, json, os, re, sys, zipfile

TRACE = re.compile(r'T (\d+) (\d) ([a-z-]+) (-?\d+) (-?\d+) (\d+) (\d+) (\d+) (\d+)')
WAIT = {'stand', 'stage', 'idle', 'bank-wait', 'convoy-wait', 'siege-wait', 'respawn-wait', 'rally'}
TARGETED = {'squad', 'cluster', 'farm', 'capture', 'stage', 'siege'}


def traces(bundle, team):
    with zipfile.ZipFile(bundle) as z:
        raw = z.read(f'team-{team}.stdout').decode('utf-8', 'replace')
    rows = []
    for m in TRACE.finditer(raw):
        r, s, a, t, hp, gems = m.groups()[:6]
        rows.append((int(r), int(s), a, int(t), int(hp), int(gems)))
    return rows


def scan_game(bundle, stats, ours):
    """ours: 'a' or 'b'. Returns a list of (kind, champion_rounds, detail)."""
    team = 'team' + ours.upper()
    rows = traces(bundle, ours)
    if not rows:
        return [], 0
    end = stats['match']['roundsStarted']
    by = collections.defaultdict(list)
    for x in rows:
        by[x[1]].append(x)
    cleared = set()
    deaths = []
    for e in stats['events']:
        if e['owner'].get('team') != team:
            continue
        if e['kind'] == 'campClear':
            cleared |= {x['target']['id'] for x in e['entries'] if isinstance(x.get('target'), dict)}
        if e['kind'] == 'death':
            deaths += [(x['timestamp']['round'], x['x'], x['y'], (x.get('target') or {}).get('kind', '?')) for x in e['entries']]
    found = []
    target_time = collections.Counter()
    for slot, L in by.items():
        L.sort()
        spans = [(a, b[0] - a[0]) for a, b in zip(L, L[1:] + [(end,)])]
        # flip-flops: runs of short spans alternating between the same two actions
        run = []
        for (row, d) in spans + [((10 ** 9, slot, '', 0, 0, 0), 99)]:
            if d <= 2 and (not run or len({x[0][2] for x in run} | {row[2]}) <= 2):
                run.append((row, d))
            else:
                acts = {x[0][2] for x in run}
                if len(run) >= 6 and len(acts) == 2:
                    found.append(('flipflop', sum(x[1] for x in run),
                                  f"slot {slot} r{run[0][0][0]}-{run[-1][0][0]} {'/'.join(sorted(acts))} t={run[0][0][3]}"))
                run = [(row, d)] if d <= 2 else []
        for row, d in spans:
            if row[2] in TARGETED and row[3] >= 0:
                target_time[row[3]] += d
            if row[2] in WAIT and d >= 25:
                found.append(('idle', d, f"slot {slot} r{row[0]} {row[2]} {d} rounds"))
        # bags held: first round with gems>0 until gems drop to 0
        since = None
        for row in L:
            if row[5] > 0 and since is None:
                since = row[0]
            elif row[5] == 0 and since is not None:
                if row[0] - since >= 150:
                    found.append(('bag', row[0] - since, f"slot {slot} r{since}-{row[0]} held a bag"))
                since = None
    for g, t in target_time.items():
        if t >= 150 and g not in cleared:
            found.append(('deadend', t, f"group {g}: {t} champion-rounds, never cleared"))
    # death hotspots: greedy clusters within 4 tiles
    left = sorted(deaths)
    while left:
        r0, x0, y0, k0 = left.pop(0)
        near = [d for d in left if abs(d[1] - x0) <= 4 and abs(d[2] - y0) <= 4]
        if len(near) >= 2:
            for d in near:
                left.remove(d)
            killers = collections.Counter([k0] + [d[3] for d in near])
            found.append(('hotspot', 60 * (len(near) + 1),
                          f"{len(near) + 1} deaths near ({x0},{y0}) from r{r0}, killed by {dict(killers)}"))
    return found, end


def main():
    bot, dirs = sys.argv[1], sys.argv[2:]
    total = collections.Counter(); count = collections.Counter(); examples = collections.defaultdict(list)
    per_map = collections.defaultdict(collections.Counter)
    games = losses = 0
    for d in dirs:
        for js in sorted(glob.glob(os.path.join(d, '*.json'))):
            tag = os.path.basename(js)[:-5]
            bundle = os.path.join(d, tag + '.repl26a')
            parts = tag.split('_')
            if not os.path.exists(bundle) or len(parts) < 3:
                continue
            first = '_'.join(parts[1:]).startswith(bot + '_')
            ours = 'a' if first else 'b'
            try:
                stats = json.load(open(js))
                found, end = scan_game(bundle, stats, ours)
            except (KeyError, zipfile.BadZipFile, json.JSONDecodeError, OSError):
                continue
            games += 1
            lost = stats['match']['outcome'] != 'team' + ours.upper()
            losses += lost
            for kind, cost, detail in found:
                w = cost * (2 if lost else 1)
                total[kind] += w; count[kind] += 1; per_map[parts[0]][kind] += w
                examples[kind].append((w, f"{tag} {'LOSS' if lost else 'win'}: {detail}"))
    print(f'{bot}: {games} games scanned, {losses} lost')
    print('\nproblems ranked by weighted champion-rounds (losses x2):')
    for kind, w in total.most_common():
        print(f'  {kind:9} {w:8}  ({count[kind]} cases)')
        for w2, ex in sorted(examples[kind], reverse=True)[:5]:
            print(f'      {w2:6}  {ex}')
    print('\nworst maps:')
    for m, c in sorted(per_map.items(), key=lambda kv: -sum(kv[1].values()))[:10]:
        print(f'  {m:22} ' + '  '.join(f'{k} {v}' for k, v in c.most_common()))


if __name__ == '__main__':
    main()
