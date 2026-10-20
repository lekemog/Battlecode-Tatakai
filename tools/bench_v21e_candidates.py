#!/usr/bin/env python3
"""Frozen local release benchmark; missing/error/timeout are never wins."""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
CAMBC = os.environ.get('CAMBC_BIN') or shutil.which('cambc') or str(ROOT/'.venv-faux/bin/cambc')
TUNING = ['x_daniel7', 'x_simon6', 'x_jame4', 'x_tarotsq21', 'x_tarot16']
HOLDOUT = ['h_mohnish', 'h_deysag', 'h_vatsal', 'h_photon', 'h_apex']

def environment():
    env = os.environ.copy()
    env.setdefault('CAMBC_CACHE', str(ROOT/'.engine-cache'))
    env.setdefault('CAMBC_OFFLINE', '1')
    env.setdefault('CAMBC_NO_UPDATE_CHECK', '1')
    env['PATH'] = ':'.join([str(ROOT/'runtime/cmake-3.31.8-linux-x86_64/bin'), str(ROOT/'runtime/ninja'), env['PATH']])
    return env

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rows_for(bot):
    rows = []
    maps = sorted((ROOT/'maps').glob('*.map26a'))
    if len(maps) != 17:
        raise RuntimeError(f'expected 17 maps, found {len(maps)}')
    out = ROOT/'results'/bot
    out.mkdir(parents=True, exist_ok=True)
    for cohort, opponents in [('tuning', TUNING), ('heldout', HOLDOUT)]:
        for opponent in opponents:
            for m in maps:
                for side in ['A', 'B']:
                    stem = f'{cohort}__{opponent}__{m.stem}__{side}'
                    a, b = (bot, opponent) if side == 'A' else (opponent, bot)
                    rows.append(dict(cohort=cohort, opponent=opponent, map=m.name, side=side,
                        a=a, b=b, replay=str(out/(stem+'.repl26a')), statistics=str(out/(stem+'.json'))))
    return rows

def summarize(bot, rows):
    groups = {}
    failures = []
    games = []
    for row in rows:
        group = groups.setdefault(row['cohort'], dict(expected=0, completed=0, wins=0, losses=0, draws=0, margin_sum=0, own_faults=0, opponent_faults=0, opponents={}, maps={}))
        group['expected'] += 1
        try:
            d = json.loads(Path(row['statistics']).read_text())
            outcome = d['match']['outcome']
            if outcome not in ['teamA', 'teamB', 'draw']:
                raise ValueError(f'unsupported outcome {outcome!r}')
            teams = {x['team']: int(x['submittedGems']) for x in d['teams']}
            own, other = ('teamA', 'teamB') if row['side'] == 'A' else ('teamB', 'teamA')
            margin = teams[own]-teams[other]
            result = 'draws' if outcome == 'draw' else 'wins' if outcome == own else 'losses'
            faults = d['diagnostics']['botFaults']
            group['own_faults'] += int(faults[own])
            group['opponent_faults'] += int(faults[other])
            group['completed'] += 1
            group[result] += 1
            group['margin_sum'] += margin
            for dimension, key in [('opponents', row['opponent']), ('maps', row['map'])]:
                cell = group[dimension].setdefault(key, dict(completed=0, wins=0, losses=0, draws=0, margin_sum=0))
                cell['completed'] += 1
                cell[result] += 1
                cell['margin_sum'] += margin
            games.append(dict(row, result=result, margin=margin, rounds=d['match']['roundsStarted'], own_faults=int(faults[own]), opponent_faults=int(faults[other]), engine_build=d['match']['engineBuildHash'], map_hash=d['match']['mapHash'], seed=d['match']['seed']))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            failures.append(dict(row, error=str(exc)))
    for group in groups.values():
        group['mean_margin'] = group['margin_sum']/group['completed'] if group['completed'] else None
        group['complete'] = group['completed'] == group['expected']
    summary = dict(bot=bot, groups=groups, failures=failures, games=games)
    (ROOT/'results'/bot/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(dict(bot=bot, groups=groups, failures=len(failures)), indent=2), flush=True)
    return not failures

def main():
    p = argparse.ArgumentParser()
    p.add_argument('bot')
    p.add_argument('--jobs', type=int, default=4)
    p.add_argument('--summarize', action='store_true')
    args = p.parse_args()
    rows = rows_for(args.bot)
    out = ROOT/'results'/args.bot
    (out/'manifest.json').write_text(json.dumps(rows, indent=2)+'\n')
    if args.summarize:
        summarize(args.bot, rows)
        return
    # Resume only files already parsable; final completeness is checked separately.
    pending = []
    for row in rows:
        try:
            data = json.loads(Path(row['statistics']).read_text())
            assert 'outcome' in data['match']
        except (OSError, ValueError, KeyError, AssertionError):
            pending.append(row)
    manifest = out/'batch.txt'
    manifest.write_text(''.join(f"{ROOT}/bots/{r['a']} {ROOT}/bots/{r['b']} {ROOT}/maps/{r['map']} {r['replay']} --statistics {r['statistics']} --json\n" for r in pending))
    freeze = dict(engine=subprocess.check_output([CAMBC, '--version'], text=True).strip(),
        release=True, maps={m.name: digest(m) for m in sorted((ROOT/'maps').glob('*.map26a'))},
        sources={str(f.relative_to(ROOT)): digest(f) for name in [args.bot]+TUNING+HOLDOUT for f in sorted((ROOT/'bots'/name/'src').rglob('*')) if f.is_file()},
        adapters={str(f.relative_to(ROOT)): digest(f) for f in sorted((ROOT/'research').rglob('*')) if f.is_file()} if (ROOT/'research').exists() else {})
    (out/'freeze.json').write_text(json.dumps(freeze, indent=2)+'\n')
    if pending:
        start = time.time()
        with (out/'runner.log').open('w') as log:
            result = subprocess.run([CAMBC, 'run-batch', str(manifest), '--jobs', str(args.jobs), '--release', '--json', '--timeout', '900', '--log-limit', '0'], cwd=ROOT, env=environment(), stdout=log, stderr=subprocess.STDOUT)
        print(f'{args.bot}: runner exit={result.returncode}, seconds={time.time()-start:.1f}', flush=True)
    if not summarize(args.bot, rows):
        raise SystemExit(1)

if __name__ == '__main__':
    main()

