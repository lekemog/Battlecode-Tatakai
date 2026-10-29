import json, re, statistics, sys
from pathlib import Path
p=(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent)/'results/audit'
rows=list(json.loads((p/'local-games.json').read_text()).values())
def norm(m):return re.sub(r'^\d\d','',m).replace('-','_')
base={(norm(r['map']),r['opponent'],r['side']):r for r in rows if r['bot']=='v50c'}
ab=[r for r in rows if r['bot']=='v50c-no-learn']
assert len(ab)==560,len(ab)
paired=[]
for r in ab:
 b=base[(norm(r['map']),r['opponent'],r['side'])]
 assert (r['seed'],r['map_hash'],r['build'])==(b['seed'],b['map_hash'],b['build'])
 paired.append({'map':r['map'],'opponent':r['opponent'],'side':r['side'],'new_map':r['new_pool_map'],'candidate_win':r['win'],'baseline_win':b['win'],'margin_delta':(r['us_submittedGems']-r['them_submittedGems'])-(b['us_submittedGems']-b['them_submittedGems']),'faults':r['us_botFault']})
filters={'all':lambda r:True,'old_layouts':lambda r:not r['new_map'],'new_layouts':lambda r:r['new_map']}
filters.update({o:lambda r,o=o:r['opponent']==o for o in sorted(set(r['opponent'] for r in paired))})
summary={}
for name,pred in filters.items():
 a=[r for r in paired if pred(r)]
 summary[name]={'games':len(a),'candidate_wins':sum(r['candidate_win'] for r in a),'baseline_wins':sum(r['baseline_win'] for r in a),'improved':sum(r['candidate_win'] and not r['baseline_win'] for r in a),'regressed':sum(r['baseline_win'] and not r['candidate_win'] for r in a),'mean_margin_delta':round(statistics.mean(r['margin_delta'] for r in a),2),'faults':sum(r['faults'] for r in a)}
(p/'ablation-comparison.json').write_text(json.dumps(summary,indent=2))
lines=['# Exploratory learned-layer ablation','','This follow-up was specified after initial benchmark saturation was observed. It is not a new untouched confirmatory holdout. Only cfg::learned changes from 1 to 0; the separate death-hazard model remains enabled. Disabling learned adjustments also changes compute cost, so differences cannot uniquely identify statistical overfitting. No weights were retrained or searched.','','| Slice | Games | Learned off wins | v50c wins | Improved cases | Regressed cases | Mean gem-margin delta |','|---|---:|---:|---:|---:|---:|---:|']
for name,s in summary.items():lines.append(f"| {name} | {s['games']} | {s['candidate_wins']} | {s['baseline_wins']} | {s['improved']} | {s['regressed']} | {s['mean_margin_delta']} |")
lines+=['','## Per-map comparison','','Each row contains eight cases: four opponents, both sides.','','| Map | Learned off wins | Baseline wins | Net |','|---|---:|---:|---:|']
for m in sorted({norm(r['map']) for r in paired}):
 a=[r for r in paired if norm(r['map'])==m]
 cw=sum(r['candidate_win'] for r in a);bw=sum(r['baseline_win'] for r in a)
 assert len(a)==8
 lines.append(f'| {m} | {cw}/8 | {bw}/8 | {cw-bw:+d} |')
lines+=['','All 560 cases have matched map hashes, default engine seeds, opponent and side. Results supplement the original 2,800-game experiment. Disabling the learned adjustments loses 29 net wins and reduces average gem margin by 61.94; retain the layer. Regression appears on both old and added layouts. This is evidence against this removal, not proof the existing model is free of overfitting. Stronger opponents and fresh seeds are still needed.']
(p/'ABLATION.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,indent=2))
