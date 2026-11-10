import csv,json,collections,random,math
from pathlib import Path
root=Path(__file__).parent
rows=list(csv.DictReader((root/'cases.csv').open()));out={};rng=random.Random(61)
for c in ['cg-role61-kite','cg-role61']:
 for o in ['v53x','v50p1','v60d']:
  base={(r['map'],r['side']):r for r in rows if r['candidate']=='v60d' and r['opponent']==o}
  cr=[r for r in rows if r['candidate']==c and r['opponent']==o]
  if len(cr)!=256 or len(base)!=256: continue
  bymap=collections.defaultdict(list);up=down=0;deltas=collections.defaultdict(list)
  for r in cr:
   b=base[r['map'],r['side']];d=int(r['win'])-int(b['win']);bymap[r['map']].append(d);up+=d>0;down+=d<0
   for k in ['margin','deaths','gold200','vesper_gold200','earnedGold','fuelExhausted','deaths200','spentGold200','vesper_deaths200','vesper_spentGold200','vesper_championDamageDone200']:
    deltas[k].append(float(r[k])-float(b[k]))
  # Resample maps, preserving both sides together; avoid treating sides as independent maps.
  vals=[sum(v)/2 for v in bymap.values()];boots=sorted(sum(rng.choices(vals,k=len(vals)))/len(vals)*100 for _ in range(5000))
  n=up+down;p=min(1.,2*sum(math.comb(n,k) for k in range(min(up,down)+1))/2**n) if n else 1.
  out[c+' vs '+o]={'maps':128,'games':256,'win_rate_delta_percentage_points':sum(vals)/len(vals)*100,'map_bootstrap_95_percent_interval':[boots[125],boots[4874]],'loss_to_win':up,'win_to_loss':down,'discordant_pair_binomial_p_unadjusted':p,'mean_metric_deltas':{k:sum(v)/len(v) for k,v in deltas.items()}}
(root/'paired.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
