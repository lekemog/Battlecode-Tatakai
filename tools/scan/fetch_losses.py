"""Download our recent real losses (replay bundle with our bot's trace log + match summary) for tools/scan.

Run on a machine that can reach the Battlecode site, after `cambc login`:
  python3 -I tools/scan/fetch_losses.py [--kind ranked|unranked|any] [--limit 100] [--all] [--push]

Files go to replays/real/ as <map>_us_<opp>.{repl26a,json} (we were side a) or <map>_<opp>_us.* (side b), the naming
tools/scan/scan.py and deaths.py expect with BOT=us:
  python3 -I tools/scan/scan.py us replays/real
  python3 -I tools/scan/deaths.py us replays/real
--all also keeps wins; --push commits replays/real and pushes the current branch so a remote session can read it.
Match fields used (matchId, map, status, teams[].name/side/result) are the ones tools/top10/*.py rely on.
"""
import json, os, re, subprocess, sys

TEAM = 'LionelMSISS'
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, 'replays', 'real')


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def cambc(*a):
    r = subprocess.run(['cambc', *a], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"cambc {' '.join(a)}: {(r.stderr or r.stdout).strip()[-300:]}")
    return r.stdout


def clean(s):
    return re.sub(r'[^A-Za-z0-9-]+', '-', s).strip('-') or 'x'


def main():
    kind, limit = arg('--kind', 'ranked'), arg('--limit', '100')
    args = ['matches', 'list', '--team', 'me', '--limit', limit, '--json']
    if kind != 'any':
        args[4:4] = ['--kind', kind]
    matches = json.loads(cambc(*args)).get('matches') or []
    os.makedirs(OUT, exist_ok=True)
    got = 0
    for m in matches:
        if m.get('status') != 'finished':
            continue
        us = next((t for t in m['teams'] if t['name'] == TEAM), None)
        them = next((t for t in m['teams'] if t['name'] != TEAM), None)
        if not us or not them or (us.get('result') == 'win' and '--all' not in sys.argv):
            continue
        mp, opp = clean(m['map']).replace('_', '-'), clean(them['name'])
        tag = f'{mp}_us_{opp}' if us['side'] == 'a' else f'{mp}_{opp}_us'
        tag += '-' + m['matchId'][:8] if os.path.exists(os.path.join(OUT, tag + '.json')) else ''
        base = os.path.join(OUT, tag)
        if os.path.exists(base + '.json'):
            continue
        try:
            cambc('matches', 'download', m['matchId'], '-o', base + '.repl26a')
            cambc('matches', 'summary', m['matchId'], '--json', '-o', base + '.json')
        except RuntimeError as e:
            print(f"skip {m['matchId']}: {e}")
            continue
        got += 1
        print(f"{tag}: {us.get('result')} vs {them['name']} on {m['map']} ({m['matchId']})", flush=True)
    print(f'{got} new games in {OUT}')
    if '--push' in sys.argv and got:
        subprocess.run(['git', '-C', REPO, 'add', OUT], check=True)
        subprocess.run(['git', '-C', REPO, 'commit', '-m', f'replays/real: {got} recent {kind} games'], check=True)
        subprocess.run(['git', '-C', REPO, 'push'], check=True)


if __name__ == '__main__':
    main()
