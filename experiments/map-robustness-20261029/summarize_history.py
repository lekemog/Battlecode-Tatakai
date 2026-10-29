import collections,json,re
from pathlib import Path
here=Path(__file__).resolve().parent
rows=json.loads((here/'historical-games.json').read_text())
assert len({r['id'] for r in rows})==len(rows)
def name(m):return re.sub(r'^\d\d','',m).replace('-','_')
cohorts=sorted({r['cohort'] for r in rows})
counts=collections.defaultdict(lambda:collections.defaultdict(lambda:[0,0]))
for r in rows:
    c=counts[name(r['map'])][r['cohort']];c[0]+=r['win'];c[1]+=1
lines=['# Map-by-map match history audit','',f'{len(rows)} distinct match IDs recovered from repository data. This covers all matching records in the inspected caches, not a complete lifetime platform export. Engine/version metadata is incomplete for legacy caches. Do not pool cohorts into a current-bot win rate.','', '| Map | '+' | '.join(cohorts)+' |','|---|'+'---:|'*len(cohorts)]
for m,cs in sorted(counts.items()):
    lines.append('| '+m+' | '+' | '.join(f'{cs[c][0]}/{cs[c][1]}' if c in cs else '—' for c in cohorts)+' |')
lines+=['','Entries are wins / games. US-features records exclude opponent/top-vs-top labels. Exact match IDs are deduplicated, preferring newer cohorts. scrim_cache.json and scrim_cache_v24z.json contain the same 20 IDs and are counted once. Other-team fish caches and third-party top-50 scouting records are excluded. Names are normalized only for display; raw names and identity remain in historical-games.json. Similar names do not establish identical map hashes across patches.','', 'Current v221 top-ten observations: quadrants 0/3; collision, expanse, packs, reverse_spiral, rows, stampede, cuts, famine and fields each 0/2. Fracture is 1/3 and guardians 1/2. These are diagnostic priorities, not statistically established map win rates. Maps with one game cannot be classified reliably.','', 'Legacy persistence: collision is 0/5 and contest 0/4 in the US-features cohort; collision is also 0/2 in each of the recovered old-ranked and current-top-ten cohorts. That recurring signal warrants replay review, while opponent strength and patch changes remain confounders. The old v24z, v25a and v25c top-four cohorts each lost 20/20; this is broad competitive weakness rather than evidence isolating one bad map.','', 'The earlier fixed-five-map 50-game study reported expanse 1/10, lanes 0/10, eight 2/10, rows 3/10, the_pack 4/10. Those prior aggregate figures are separate from the '+str(len(rows))+' recovered per-game records; their missing per-game source files are not fabricated into this audit.','', 'The live team profile and match-history interface confirm a much larger lifetime history. The interface inspected here exposes match groups and filters, with no team-level map export found; the daily database ZIPs cover all teams and are very large. This report does not claim that its cached sample represents every platform win/loss. A full per-match team export with map hash, bot version, patch, opponent and side is still needed to estimate lifetime map performance.']
(here/'map-history.md').write_text('\n'.join(lines)+'\n')
print({c:(sum(r['win'] for r in rows if r['cohort']==c),sum(r['cohort']==c for r in rows)) for c in cohorts})
