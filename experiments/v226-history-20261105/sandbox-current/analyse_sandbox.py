import json,hashlib,statistics,collections,sys
from pathlib import Path
p=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent;out=p/'sandbox-current'
plan=json.loads((out/'plan.json').read_text());index=json.loads((out/'index.json').read_text())
cache_path=out/'compact.json';cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
for case in index:
 if case['tag'] in cache:continue
 path=out/(case['tag']+'.json')
 if not path.exists():continue
 try:s=json.loads(path.read_text())
 except json.JSONDecodeError:continue
 m=s['match'];assert m['engineVersion']==plan['expected_engine'];assert m['engineBuildHash']==plan['expected_build']
 r=dict(case,win=m['outcome']==case['side'],engine=m['engineVersion'],build=m['engineBuildHash'],seed=m['seed'],map_hash=m['mapHash'],rounds=m['roundsStarted'])
 for label,side in [('us',case['side']),('them','teamB' if case['side']=='teamA' else 'teamA')]:
  for k in ['submittedGems','deaths']:
   r[label+'_'+k]=sum(float(c['metrics'].get(k,0)) for c in s['champions'] if c['team']==side)
  for k in ['botFault','fuelExhausted']:
   r[label+'_'+k]=sum(len(e['entries']) for e in s['events'] if e['kind']==k and e['owner'].get('team')==side)
 cache[case['tag']]=r
cache_path.write_text(json.dumps(cache,indent=2));rows=list(cache.values())
print('Parsed completed cases:',len(rows),'/',len(index),flush=True)
if len(rows)!=len(index):sys.exit(0)
assert len(rows)==480
base={(r['opp'],r['map'],r['side']):r for r in rows if r['bot']=='v50h5e'}
summary={};paired={}
for bot in ['v50h5e','chatgpt-v50h5e-history']:
 summary[bot]={}
 for opp in plan['opponents']:
  a=[r for r in rows if r['bot']==bot and r['opp']==opp];assert len(a)==80
  summary[bot][opp]={'games':80,'wins':sum(r['win'] for r in a),'banked':round(statistics.mean(r['us_submittedGems'] for r in a),2),'margin':round(statistics.mean(r['us_submittedGems']-r['them_submittedGems'] for r in a),2),'deaths':round(statistics.mean(r['us_deaths'] for r in a),2),'fault_events':sum(r['us_botFault'] for r in a),'fuel_events':sum(r['us_fuelExhausted'] for r in a)}
  if bot!='v50h5e':
   gains=[];losses=[]
   for r in a:
    b=base[r['opp'],r['map'],r['side']];assert (r['seed'],r['map_hash'],r['build'])==(b['seed'],b['map_hash'],b['build'])
    if r['win'] and not b['win']:gains.append(r['tag'])
    if b['win'] and not r['win']:losses.append(r['tag'])
   paired[opp]={'gains':gains,'losses':losses}
lines=['# Sandbox against current repository bots — 5 November 2026','', '**480 completed local release-mode games**, 40 archived benchmark maps, both sides. Frozen source snapshot 03b34544c02d0e9b501183f5d1f4a60759ceec9f. Candidate is the unchanged PR #75 build from v226. No tuning during the run.','', 'CLI 5.0.0 was checked against the package index as the latest available release. Every game is engine 3.0.0, build '+plan['expected_build']+'. Engine/build assertions fail closed.','', '| Policy | Opponent | Wins / 80 | Mean banked | Mean gem margin | Mean deaths | Fault events | Fuel events |','|---|---|---:|---:|---:|---:|---:|---:|']
for bot,opps in summary.items():
 for opp,s in opps.items():lines.append(f"| {bot} | {opp} | {s['wins']} | {s['banked']} | {s['margin']} | {s['deaths']} | {s['fault_events']} | {s['fuel_events']} |")
lines+=['','## Matched candidate changes','','| Opponent | Converted losses | Lost baseline wins |','|---|---:|---:|']
for opp,d in paired.items():lines.append(f"| {opp} | {len(d['gains'])} | {len(d['losses'])} |")
lines+=['','## Per-map net wins relative to v226','','Each cell sums both matched sides.','','| Map | vs v226 | vs v51d | vs early pack |','|---|---:|---:|---:|']
for m in sorted({r['map'] for r in rows}):
 vals=[]
 for opp in plan['opponents']:
  a=[r for r in rows if r['bot']!='v50h5e' and r['map']==m and r['opp']==opp];vals.append(str(sum(int(r['win'])-int(base[r['opp'],m,r['side']]['win']) for r in a)))
 lines.append('| '+m+' | '+' | '.join(vals)+' |')
lines+=['','## Interpretation and limits','','v226/v50h5e is the live baseline reported by GitHub; v51d is the latest recommended development candidate, not asserted live. v50p1 is the documented local rush stress opponent. Active platform submission was not independently queried in this sandbox.','', 'This covers the pinned 40-map benchmark, NOT all 128 active maps. CLI map download failed and the direct map listing required authentication; browser retrieval did not complete. Map bytes were recovered from the repository. These inspected maps are not blind holdouts. Default deterministic seeds do not create independent repeat evidence.','', 'Use these results as a current-engine regression/stress screen. No unranked ladder groups, activation or deployment occurred. The testing guide requires stronger pinned panels for retreat changes; no promotion from these local results alone. Candidate source was unchanged throughout. The initial scheduler was stopped during setup before any games completed, to finish opponent compilation without overlapping build jobs; the completed run retains all 480 planned cases.']
(out/'RESULTS.md').write_text('\n'.join(lines)+'\n')
builds={}
for bot in ['v50h5e','chatgpt-v50h5e-history','v51d','v50p1']:
 b=p/'bots'/bot;flag=next(l for l in (b/'.cambc/build-release/CMakeCache.txt').read_text().splitlines() if l.startswith('CAMBC_DEBUG:'));assert flag.endswith('=OFF')
 builds[bot]={'release_wasm_sha256':hashlib.sha256((b/'.cambc/build-release/bot.wasm').read_bytes()).hexdigest(),'sources':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (b/'src').iterdir() if f.is_file()}}
(out/'validation.json').write_text(json.dumps({'summary':summary,'paired':paired,'builds':builds,'expected_cases':480,'completed_cases':len(rows),'all_fault_events':sum(r['us_botFault']+r['them_botFault'] for r in rows)},indent=2))
print(json.dumps(summary,indent=2))
