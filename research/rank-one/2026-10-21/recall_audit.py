"""Audit recall starts and channel exits from recall_extract.mjs output.
Usage: python recall_audit.py 'replays/*/recall_decoded.json' output.json
All r fields are native engine game-round keys, not snapshot indices.
"""
import collections
import glob
import hashlib
import json
from pathlib import Path
import statistics
import sys

out = []
for name in sorted(glob.glob(sys.argv[1])):
    path = Path(name)
    data = json.loads(path.read_text())
    assert data['version'] == 'v1_0_1', 'Keep engine cohorts separate'
    exits = [t for t in data['transitions'] if t['before']['channelType'] == 1 and t['after']['channelType'] == 0]
    starts = data['recalls']
    keys = [(s['r'], s['input'], s['champion']['entity']['index']) for s in starts]
    assert len(keys) == len(set(keys)), 'Duplicate native recall events'
    rows = []
    for s in starts:
        c = s['previous']
        cid = c['entity']['index']
        end = next((e for e in exits if e['id'] == cid and e['input'] > s['input']), None)
        completed = bool(end and end['kind'] == 4 and end['before']['channelTimer'] == 0 and end['after']['alive'])
        rows.append(dict(round=s['r'], input=s['input'], champion_id=cid, champion_type=c['type'],
            hp=c['health'], max_hp=c['maxHealth'], gold=c['gold'], gems=c['gems'],
            position=c['position'], timer=s['champion']['channelTimer'],
            end_round=end['r'] if end else None, end_kind=end['kind'] if end else None,
            end_timer=end['before']['channelTimer'] if end else None, completed=completed,
            end_position=end['after'].get('position') if end else None,
            end_gems=end['after']['gems'] if end else None))
    hp = [x['hp']/x['max_hp'] for x in rows]
    out.append(dict(match_id=path.parent.name, engine=data['version'], final_round=data['rounds'][-1]['round'],
        replay_sha256=hashlib.sha256(path.with_name('replay.repl26a').read_bytes()).hexdigest(),
        starts=len(rows), completions=sum(x['completed'] for x in rows),
        manual_cancellations=sum(x['end_kind'] == 16 for x in rows),
        damage_interruptions=sum(x['end_kind'] in (5, 6) for x in rows),
        hp_median=statistics.median(hp), high_hp_starts=sum(x >= .8 for x in hp),
        starts_with_gems=sum(x['gems'] > 0 for x in rows), home_timer_starts=sum(x['timer'] == 3 for x in rows),
        recalls=rows))
hashes = [x['replay_sha256'] for x in out]
assert len(hashes) == len(set(hashes)), 'Duplicate replay content'
Path(sys.argv[2]).write_text(json.dumps(out, indent=2)+'\n')
for x in out:
    print(x['match_id'], x['starts'], x['completions'], x['manual_cancellations'], x['damage_interruptions'])
