"""Describe native recall starts; does not infer a policy from positive examples.
Run beside recall_evidence.json. Threshold 172 is a previous descriptive minimum,
not a fitted decision threshold or recommended bot constant.
"""
import collections
import hashlib
import json
from pathlib import Path

root = Path(__file__).parent
source = root / 'recall_evidence.json'
games = json.loads(source.read_text())
assert len({g['match_id'] for g in games}) == len(games)
assert len({g['replay_sha256'] for g in games}) == len(games)
buckets = collections.defaultdict(lambda: dict(starts=0, completed=0, manual_cancel=0, damage_interrupt=0))
counterexamples = []
for g in games:
    assert g['engine'] == 'v1_0_1'
    seen = set()
    for r in g['recalls']:
        key = (r['round'], r['input'], r['champion_id'])
        assert key not in seen
        seen.add(key)
        hp = r['hp'] / r['max_hp']
        key = ('hp_below_50' if hp < .5 else 'hp_at_least_50') + ('_gold_at_least_172' if r['gold'] >= 172 else '_gold_below_172')
        b = buckets[key]
        b['starts'] += 1
        b['completed'] += int(r['completed'])
        b['manual_cancel'] += int(r['end_kind'] == 16)
        b['damage_interrupt'] += int(r['end_kind'] in (5, 6))
        if hp >= .5 and r['gold'] < 172:
            counterexamples.append(dict(match_id=g['match_id'], replay_sha256=g['replay_sha256'], **r))
output = dict(question='Can HP below 50% or gold at least 172 explain every observed recall start?',
    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), engine='v1_0_1', fish_side='B',
    games=len(games), starts=sum(b['starts'] for b in buckets.values()), buckets=dict(buckets),
    outside_both_conditions=counterexamples,
    limits=['Positive recall starts only; no non-recall comparison states.',
            'Selected five-game single-opponent series; no new games.',
            '172 gold is a descriptive probe, not a causal or optimal threshold.',
            'Submission identifiers remain unknown.'])
assert sum(b['completed']+b['manual_cancel']+b['damage_interrupt'] for b in buckets.values()) == output['starts']
(root/'recall_trigger_evidence.json').write_text(json.dumps(output, indent=2)+'\n')
print(json.dumps({k:v for k,v in output.items() if k != 'outside_both_conditions'}, indent=2))
print('Outside both conditions:', len(counterexamples))
