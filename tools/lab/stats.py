import json,glob,sys,collections,os
bot=sys.argv[1];d=sys.argv[2]
tot=collections.defaultdict(float);n=0;w=0
for f in glob.glob(d+'/*/*.json'):
    j=json.load(open(f))
    if 'agg' not in j: continue
    b=os.path.basename(f)[:-5];m,first,second=b.split('_',2)
    us='teamA' if first==bot else 'teamB';them='teamB' if us=='teamA' else 'teamA'
    n+=1;w+=j['match']['outcome']==us
    for k,v in j['agg'].get(us,{}).items(): tot['us_'+k]+=v
    for k,v in j['agg'].get(them,{}).items(): tot['them_'+k]+=v
print(bot,'games',n,'wins',w)
print(' per game us:',{k[3:]:round(v/n,1) for k,v in tot.items() if k.startswith('us_')})
print(' per game them:',{k[5:]:round(v/n,1) for k,v in tot.items() if k.startswith('them_')})
# error counts per game (ours)
import glob as _g,collections as _c
ec=_c.Counter();ng=0
for f in _g.glob(d+'/*/*.json'):
    j=json.load(open(f))
    if 'errs' in j:
        ng+=1
        for k,v in j['errs'].items(): ec[k]+=v
print(' errors per game (ours, by engine code):',{k:round(v/max(1,ng),2) for k,v in ec.items()})
