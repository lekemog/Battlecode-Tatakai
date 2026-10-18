"""Summarize DOM-exported series; no network access or platform mutations.

Usage: python summarize_maps.py series.json cohort.json output.json
Missing tiebreak scores stay null. A/B order comes from the observed series link label.
"""
import collections
import json
import re
import sys


def summarize(series, cohort):
    labels = {c['url']: c['label'] for c in cohort}
    rows = []
    seen = set()
    for s in series:
        label = labels[s['url']]
        a, b = label.removeprefix('View ').removesuffix(' match').split(' vs ')
        assert (a == 'LionelMSISS') != (b == 'LionelMSISS')
        us_first = a == 'LionelMSISS'
        ver = int(re.search(r'Bot version (\d+)', s['text'])[1])
        chunks = re.findall(r'\n([1-5])\n([^\n]+)\n([\d,]+) rounds\n([^\n]+) wins\n([^\n]+)', s['text'])
        assert len(chunks) == len(s['links']) == 5
        for i, map_name, duration, winner, outcome in chunks:
            mid = s['links'][int(i)-1].rsplit('/', 1)[-1]
            assert mid not in seen
            seen.add(mid)
            score = re.search(r'(\d+) : (\d+)', outcome)
            scores = list(map(int, score.groups())) if score else [None, None]
            if not us_first:
                scores.reverse()
            won = winner == 'LionelMSISS'
            if score:
                assert won == (scores[0] > scores[1]), (mid, scores, winner)
            rows.append(dict(series=s['url'], match_id=mid, version=ver,
                             opponent=b if us_first else a, side='a' if us_first else 'b',
                             map=map_name, rounds=int(duration.replace(',', '')),
                             win=won, ours=scores[0], theirs=scores[1], outcome=outcome,
                             opponent_version=None, detail_status='not_downloaded'))
    return rows


def aggregate(rows):
    result = []
    for version in sorted({r['version'] for r in rows}, reverse=True):
        for name in sorted({r['map'] for r in rows if r['version'] == version}):
            q = [r for r in rows if r['version'] == version and r['map'] == name]
            margins = [r['ours']-r['theirs'] for r in q if r['ours'] is not None]
            result.append(dict(version=version, map=name, n=len(q), wins=sum(r['win'] for r in q),
                               mean_gem_margin=sum(margins)/len(margins) if margins else None,
                               scored_n=len(margins), rounds=[r['rounds'] for r in q]))
    return result


if __name__ == '__main__':
    rows = summarize(json.load(open(sys.argv[1])), json.load(open(sys.argv[2])))
    out = dict(matches=rows, by_version_map=aggregate(rows))
    json.dump(out, open(sys.argv[3], 'w'), indent=2)
    for r in out['by_version_map']:
        print(r)
