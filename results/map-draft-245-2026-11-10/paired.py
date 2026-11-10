from pathlib import Path
import csv,json,random,collections
r=Path(__file__).parent;rows=list(csv.DictReader((r/'cases.csv').open()));rng=random.Random(245);out={}
base={(v['opponent'],v['map'],v['side']):v for v in rows if v['candidate']=='v61j'}
for c in ['cg-md245-plan','cg-md245-react']:
 for o in ['v61j','v50p1']:
  rs=[v for v in rows if v['candidate']==c and v['opponent']==o]
  if len(rs)!=256:continue
  by=collections.defaultdict(list);metrics=collections.defaultdict(list);up=down=0
  for v in rs:
   b=base[o,v['map'],v['side']];d=int(v['win'])-int(b['win']);up+=d>0;down+=d<0;by[v['map']].append(d)
   for k in ['margin','deaths','earnedGold50','earnedGold100','earnedGold200','spentGold200','fuelExhausted']:metrics[k].append(float(v[k])-float(b[k]))
  vals=[sum(v)/len(v) for v in by.values()];boots=sorted(sum(rng.choices(vals,k=len(vals)))/len(vals)*100 for _ in range(5000))
  out[c+' vs '+o]={'maps':len(by),'pairs':len(rs),'loss_to_win':up,'win_to_loss':down,'win_rate_change_pp':sum(vals)/len(vals)*100,'map_cluster_bootstrap95_pp':[boots[125],boots[4874]],'mean_metric_changes':{k:sum(v)/len(v) for k,v in metrics.items()}}
(r/'paired.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
