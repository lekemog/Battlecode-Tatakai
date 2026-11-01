"""Fixed real-opponent panel: test a submitted version against frozen versions of real teams, paired with the live bot.

Patch 2.0.0 (CLI 4.0.0) lets an unranked match group use an opponent's historical bot (`--source-group`), so the
same opponents, maps and sides can be replayed for every candidate. That gives the paired, ladder-like test the local
bench cannot (bench bots are frozen pre-patch code that we beat 88% of the time).

Setup: write tools/panel/panel.json (see panel.example.json): one entry per opponent with its team UUID, a previous
match-group UUID or link that pins its bot version, five maps and five sides. Then, logged in with `cambc login`:

  python3 -I tools/panel/panel.py run LABEL VERSION [--pin BASE_LABEL]
      make VERSION live, play the panel, restore the old live version. With --pin, each opponent plays the exact bot
      version it used in BASE_LABEL's run (its match group is passed as --source-group), so a baseline run and a
      candidate run face identical opponents. Entries without "source_group" and no --pin use the opponent's current bot.
  python3 -I tools/panel/panel.py compare LABEL_A LABEL_B   # paired per-game comparison

Results go to results/panel/LABEL.json. Uses only official CLI commands. Run it from ONE place at a time: scrims
always play whatever version is live, so a second submitter would corrupt the test.
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, 'results', 'panel')
POLL = 30


def cli(*args, parse=True):
    r = subprocess.run(['cambc', *args] + (['--json'] if parse else []), capture_output=True, text=True)
    if r.returncode != 0:
        msg = (r.stderr or r.stdout).strip()
        raise RuntimeError(f"cambc {' '.join(args)} failed: {msg[-400:]}")
    if not parse:
        return r.stdout
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"cambc {' '.join(args)}: expected JSON, got: {r.stdout[:400]}")


def find(obj, *keys):
    """First value under any of `keys`, searching nested dicts and lists (the CLI's JSON shapes are not documented)."""
    if isinstance(obj, dict):
        for k in keys:
            if k in obj:
                return obj[k]
        for v in obj.values():
            x = find(v, *keys)
            if x is not None:
                return x
    elif isinstance(obj, list):
        for v in obj:
            x = find(v, *keys)
            if x is not None:
                return x
    return None


def live_version():
    data = cli('submissions', 'list')
    rows = data if isinstance(data, list) else find(data, 'submissions', 'versions', 'items') or []
    for row in rows:
        if any(row.get(k) for k in ('live', 'selected', 'active', 'isLive', 'isSelected')):
            return str(find(row, 'version', 'number', 'id'))
    raise RuntimeError(f'could not tell which version is live from: {json.dumps(data)[:400]}')


def wait_group(gid, n=5, timeout=3600):
    """Finished matches of a group, via `cambc matches list` (the shape tools/top10/midtest.sh relies on)."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        d = cli('matches', 'list', '--team', 'me', '--kind', 'unranked', '--limit', '100')
        ms = [m for m in (d.get('matches') or []) if m.get('groupId') == gid]
        if len(ms) >= n and all(m.get('status') == 'finished' for m in ms):
            return ms
        time.sleep(POLL)
    raise RuntimeError(f'group {gid}: not finished after {timeout}s')


def score(summary, side):
    me, them = ('teamA', 'teamB') if side == 'a' else ('teamB', 'teamA')
    gems = {t['team']: int(t['submittedGems']) for t in summary['teams']}
    count = lambda kind, team: sum(len(e['entries']) for e in summary['events'] if e['kind'] == kind and e['owner'].get('team') == team)
    return {'win': summary['match']['outcome'] == me, 'gems': gems[me], 'opp_gems': gems[them],
            'deaths': count('death', me), 'kills': count('kill', me), 'rounds': summary['match']['roundsStarted']}


def run(label, version, pin=None):
    panel = json.load(open(os.environ.get('PANEL_FILE') or os.path.join(HERE, 'panel.json')))
    os.makedirs(OUT, exist_ok=True)
    pinned = json.load(open(os.path.join(OUT, f'{pin}.json'))).get('groups', {}) if pin else {}
    path = os.path.join(OUT, f'{label}.json')
    result = json.load(open(path)) if os.path.exists(path) else {'label': label, 'version': version, 'games': {}, 'groups': {}}
    result.setdefault('groups', {})
    before = live_version()
    print(f'live before: {before}; activating {version}', flush=True)
    cli('submissions', 'activate', str(version))
    try:
        for opp in panel['opponents']:
            key = opp['name']
            if key in result['games']:
                continue   # resumable: finished opponents are kept
            sides = opp['sides']
            source = pinned.get(key) or opp.get('source_group')
            args = ['match-groups', 'create', opp['team_id'], '--maps', ','.join(opp['maps']), '--sides', ','.join(sides)]
            if source:
                args += ['--source-group', source]
            for attempt in range(40):   # the shared quota refills over time
                try:
                    g = cli(*args)
                    break
                except RuntimeError as err:
                    if '409' in str(err):
                        g = None   # the team left the ladder: skip this opponent (compare() only uses opponents present in both runs)
                        break
                    if '400' in str(err) or attempt == 39:
                        raise   # a bad request (e.g. repeated maps) will not fix itself
                    print(f'{key}: create failed ({str(err)[-120:]}), retrying in 60s', flush=True)
                    time.sleep(60)
            if g is None:
                print(f'{key}: skipped (team no longer taking part)', flush=True)
                result.setdefault('skipped', []).append(key)
                json.dump(result, open(path, 'w'), indent=1)
                continue
            gid = str(find(g, 'groupId', 'id', 'uuid'))
            result['groups'][key] = gid
            json.dump(result, open(path, 'w'), indent=1)
            print(f'{key}: group {gid}' + (f' (opponent pinned to {source})' if source else ''), flush=True)
            matches = wait_group(gid)
            games = []
            for i, m in enumerate(matches):
                mid = str(find(m, 'matchId', 'id', 'uuid'))
                sp = os.path.join(OUT, 'summaries', f'{mid}.json')
                os.makedirs(os.path.dirname(sp), exist_ok=True)
                cli('matches', 'summary', mid, '-o', sp, '--json', parse=False)
                # The list is not guaranteed to be in map order: match on the map's name when the entry carries one.
                name = str(find(m, 'map', 'mapName', 'mapSlug') or '')
                j = next((k for k, mp in enumerate(opp['maps']) if mp == name or mp.lstrip('0123456789') == name), i)
                games.append({'map': opp['maps'][j], 'side': sides[j], 'match': mid, **score(json.load(open(sp)), sides[j])})
            games.sort(key=lambda x: opp['maps'].index(x['map']))
            result['games'][key] = games
            json.dump(result, open(path, 'w'), indent=1)
            print(f"{key}: {sum(x['win'] for x in games)}/5 wins", flush=True)
    finally:
        print(f'restoring live version {before}', flush=True)
        cli('submissions', 'activate', before)


def compare(a, b):
    A = json.load(open(os.path.join(OUT, f'{a}.json')))['games']
    B = json.load(open(os.path.join(OUT, f'{b}.json')))['games']
    tot = {a: {'win': 0, 'margin': 0, 'deaths': 0, 'kills': 0}, b: {'win': 0, 'margin': 0, 'deaths': 0, 'kills': 0}}
    better = worse = n = 0
    for opp in sorted(set(A) & set(B)):
        for x, y in zip(A[opp], B[opp]):
            n += 1
            for lab, g in ((a, x), (b, y)):
                tot[lab]['win'] += g['win']; tot[lab]['margin'] += g['gems'] - g['opp_gems']
                tot[lab]['deaths'] += g['deaths']; tot[lab]['kills'] += g['kills']
            d = (x['gems'] - x['opp_gems']) - (y['gems'] - y['opp_gems'])
            better += d > 0; worse += d < 0
            flag = '' if x['win'] == y['win'] else ('  <- ' + (a if x['win'] else b) + ' wins')
            print(f"{opp:20} {x['map']:20} {x['side']}  {a} {x['gems']:5}-{x['opp_gems']:<5} {b} {y['gems']:5}-{y['opp_gems']:<5}{flag}")
    print(f'\n{n} paired games')
    for lab in (a, b):
        t = tot[lab]
        print(f"{lab:12} wins {t['win']:3}  mean margin {t['margin']/max(1,n):+7.1f}  deaths {t['deaths']/max(1,n):5.1f}  kills {t['kills']/max(1,n):5.1f}")
    print(f'{a} margin better in {better} games, worse in {worse}')


if __name__ == '__main__':
    if len(sys.argv) in (4, 6) and sys.argv[1] == 'run':
        run(sys.argv[2], sys.argv[3], sys.argv[5] if len(sys.argv) == 6 and sys.argv[4] == '--pin' else None)
    elif len(sys.argv) == 4 and sys.argv[1] == 'compare':
        compare(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
