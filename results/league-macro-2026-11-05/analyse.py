"""Summarise the frozen macro experiment. Run after cambc run-batch finishes.

python results/<report>/analyse.py /path/to/lab /path/to/raw-output
The raw-output directory must also contain this report's index.json and plan.json.
"""
import argparse
import hashlib
import json
import statistics
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('project', type=Path)
ap.add_argument('output', type=Path)
args = ap.parse_args()
root, out = args.project.resolve(), args.output.resolve()
plan = json.loads((out / 'plan.json').read_text())
index = json.loads((out / 'index.json').read_text())
assert len(index) == 320
rows = []
for case in index:
    path = out / (case['tag'] + '.json')
    if not path.exists():
        continue
    s = json.loads(path.read_text())
    m = s['match']
    assert m['engineVersion'] == plan['expected_engine']
    assert m['engineBuildHash'] == plan['expected_build']
    r = dict(case, win=m['outcome'] == case['side'], outcome=m['outcome'],
             engine=m['engineVersion'], build=m['engineBuildHash'], seed=m['seed'],
             map_hash=m['mapHash'], rounds=m['roundsStarted'])
    for label, side in [('us', case['side']), ('them', 'teamB' if case['side'] == 'teamA' else 'teamA')]:
        champions = [c for c in s['champions'] if c['team'] == side]
        for metric in ['submittedGems', 'collectedGems', 'deaths', 'earnedGold']:
            r[label + '_' + metric] = sum(float(c['metrics'].get(metric, 0)) for c in champions)
        events = [e for e in s['events'] if e['owner'].get('team') == side]
        for kind in ['botFault', 'fuelExhausted']:
            r[label + '_' + kind] = sum(len(e['entries']) for e in events if e['kind'] == kind)
        losses = [int(e['value']) for g in events if g['kind'] == 'gemLoss' for e in g['entries']]
        deposits = [e for g in events if g['kind'] == 'gemSubmission' for e in g['entries']]
        deaths = [e for g in events if g['kind'] == 'death' for e in g['entries']]
        r[label + '_lostGems'] = sum(losses)
        r[label + '_largeBagLosses'] = sum(x >= 40 for x in losses)
        r[label + '_earlyDeaths'] = sum(e['timestamp']['round'] <= 200 for e in deaths)
        r[label + '_firstBank'] = min((e['timestamp']['round'] for e in deposits), default=None)
    rows.append(r)
print('Completed:', len(rows), '/', len(index), flush=True)
if len(rows) != len(index):
    raise SystemExit(0)
(out / 'compact.json').write_text(json.dumps(rows, indent=2) + '\n')
summary, paired = {}, {}
base = {(r['opp'], r['map'], r['side']): r for r in rows if r['bot'] == plan['baseline']}
for bot in [plan['baseline'], plan['candidate']]:
    summary[bot] = {}
    for opp in plan['opponents']:
        a = [r for r in rows if r['bot'] == bot and r['opp'] == opp]
        assert len(a) == 80
        d = dict(games=len(a), wins=sum(r['win'] for r in a),
                 margin=round(statistics.mean(r['us_submittedGems'] - r['them_submittedGems'] for r in a), 3),
                 no_bank=sum(r['us_firstBank'] is None for r in a),
                 fault_events=sum(r['us_botFault'] for r in a),
                 fuel_events=sum(r['us_fuelExhausted'] for r in a))
        for metric in ['submittedGems', 'deaths', 'lostGems', 'earlyDeaths', 'largeBagLosses']:
            d[metric] = round(statistics.mean(r['us_' + metric] for r in a), 3)
        ordinary = [r for r in a if r['map'] != '01boss-battle']
        d['lostGems_excluding_boss_battle'] = round(statistics.mean(r['us_lostGems'] for r in ordinary), 3)
        summary[bot][opp] = d
        if bot != plan['baseline']:
            p = {'gains': [], 'losses': [], 'changed_metrics': []}
            for r in a:
                b = base[(opp, r['map'], r['side'])]
                assert (r['seed'], r['map_hash'], r['build']) == (b['seed'], b['map_hash'], b['build'])
                if r['win'] and not b['win']:
                    p['gains'].append(r['tag'])
                if b['win'] and not r['win']:
                    p['losses'].append(r['tag'])
                if any(r[k] != b[k] for k in ['us_submittedGems', 'them_submittedGems', 'us_deaths', 'us_lostGems', 'rounds']):
                    p['changed_metrics'].append(r['tag'])
            paired[opp] = p
builds = {}
for bot in [plan['baseline'], plan['candidate'], *plan['opponents']]:
    b = root / 'bots' / bot
    debug_flag = next(line for line in (b / '.cambc/build-release/CMakeCache.txt').read_text().splitlines() if line.startswith('CAMBC_DEBUG:'))
    assert debug_flag.endswith('=OFF'), debug_flag
    builds[bot] = {'release_wasm_sha256': hashlib.sha256((b / '.cambc/build-release/bot.wasm').read_bytes()).hexdigest(),
                   'sources': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((b / 'src').iterdir()) if f.is_file()}}
changed = [name for name, h in builds[plan['baseline']]['sources'].items() if builds[plan['candidate']]['sources'][name] != h]
assert changed == ['brain.cpp'], changed
maps = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((root / 'maps-sandbox').glob('*.map26a'))}
assert maps == plan['maps']
validation = {'summary': summary, 'paired': paired, 'builds': builds, 'maps': maps,
              'completed_cases': len(rows), 'all_fault_events': sum(r['us_botFault'] + r['them_botFault'] for r in rows),
              'all_fuel_events': sum(r['us_fuelExhausted'] + r['them_fuelExhausted'] for r in rows)}
(out / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
lines = ['# Frozen sandbox results', '', '| Policy | Opponent | Wins / 80 | Banked | Gem margin | Deaths | Lost gems | Lost gems except boss map | Faults | Fuel events |',
         '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for bot, opponents in summary.items():
    for opp, d in opponents.items():
        lines.append(f"| {bot} | {opp} | {d['wins']} | {d['submittedGems']} | {d['margin']} | {d['deaths']} | {d['lostGems']} | {d['lostGems_excluding_boss_battle']} | {d['fault_events']} | {d['fuel_events']} |")
lines += ['', '| Opponent | Converted losses | Lost baseline wins | Games with changed recorded metrics |', '|---|---:|---:|---:|']
for opp, d in paired.items():
    lines.append(f"| {opp} | {len(d['gains'])} | {len(d['losses'])} | {len(d['changed_metrics'])} |")
lines += ['', '## Per-map candidate minus baseline wins', '', '| Map | vs v226 | vs early pack |', '|---|---:|---:|']
for m in sorted({r['map'] for r in rows}):
    deltas = []
    for opp in plan['opponents']:
        a = [r for r in rows if r['bot'] == plan['candidate'] and r['map'] == m and r['opp'] == opp]
        deltas.append(str(sum(int(r['win']) - int(base[opp, m, r['side']]['win']) for r in a)))
    lines.append('| ' + m + ' | ' + ' | '.join(deltas) + ' |')
lines += ['', 'The 40 archived maps are an inspected stress set, not blind holdouts or all 128 active maps. Both sides are coupled. Default seeds are deterministic. These are local games, not new ladder scrims. No live slot was used. Gem-loss sums can count recirculated gems; they are not unique destroyed resources. A lower death count alone does not establish better play. Stronger-opponent panels remain required for a combat policy.']
(out / 'RESULTS.md').write_text('\n'.join(lines) + '\n')
print(json.dumps(summary, indent=2))
