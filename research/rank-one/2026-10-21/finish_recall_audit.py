"""Join native recall starts to conservative score bounds in the five-game study.

Run beside recall_evidence.json and series_evidence.json. Outputs finish_recall_evidence.json.
Score transitions are round-boundary observations; only transitions strictly earlier
than the native action round contribute to the score lower bound. This is not a
pathfinder or a counterfactual simulator.
"""
import hashlib
import json
from pathlib import Path

root = Path(__file__).parent
recall_path = root / 'recall_evidence.json'
series_path = root / 'series_evidence.json'
recalls = json.loads(recall_path.read_text())
series = json.loads(series_path.read_text())
index = {s['id']: s for s in series}
assert len(index) == len(series)
assert len({s['replay_sha256'] for s in recalls}) == len(recalls)
events = []
eligible = 0
for game in recalls:
    s = index[game['match_id']]
    assert game['engine'] == s['engine'] == 'v1_0_1'
    assert game['replay_sha256'] == s['sha256']
    changes = s['score_changes']
    assert all(a[1][1] <= b[1][1] for a, b in zip(changes, changes[1:]))
    assert game['final_round'] == s['final_round']
    keys = set()
    for r in game['recalls']:
        key = (r['round'], r['input'], r['champion_id'])
        assert key not in keys
        keys.add(key)
        eligible += 1
        previous = [x for x in changes if x[0] < r['round']]
        score_round, score = previous[-1] if previous else (None, [0, 0])
        if score[1] + r['gems'] < 1000:
            continue
        own_banks = [b for b in s['banks'] if b['team'] == 1 and b['id'] == r['champion_id'] and b['r'] > r['round']]
        final_banks = [b for b in s['banks'] if b['team'] == 1 and b['r'] == s['final_round']]
        events.append(dict(match_id=s['id'], replay_sha256=s['sha256'], engine=s['engine'], fish_side='B',
            recall=r, prior_score_observed_round=score_round, prior_banked_score=score[1],
            banked_plus_carrier=score[1]+r['gems'], next_carrier_bank=own_banks[0] if own_banks else None,
            final_round=s['final_round'], final_score=s['gems'], final_bank_observations=final_banks))
output = dict(question='Does Fish recall with an individually sufficient winning bag?',
    games=len(recalls), native_recall_starts=eligible, qualifying_events=len(events),
    source_file_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (recall_path, series_path)},
    events=events,
    limits=['No legal delivery ETA or counterfactual replay.', 'No new independent games.',
            'Bank timestamps are round-boundary observations; recall times are native action rounds.',
            'Fish and opponent submission IDs remain unknown.'])
(root/'finish_recall_evidence.json').write_text(json.dumps(output, indent=2)+'\n')
print(json.dumps(output, indent=2))
