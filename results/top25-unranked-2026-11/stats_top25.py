import json,os,collections,glob
ME='9c16b699-cad2-453e-8042-dae23ff934d8'
L={t['teamId']:(t['rank'],t['name']) for t in json.load(open('ladder.json'))['teams']}
keep=json.load(open('keep.json'))
def at(runs,r):
    n=0
    for x in runs:
        n+=x['duration']
        if r<n: return float(x['value'])
    return float(runs[-1]['value']) if runs else 0.0
rows=[]
for m in keep:
    p='sum/%s.json'%m['matchId']
    if not os.path.exists(p): continue
    try:j=json.load(open(p))
    except: continue
    me=[t for t in m['teams'] if t['teamId']==ME][0]; op=[t for t in m['teams'] if t['teamId']!=ME][0]
    ms='teamA' if me['side']=='a' else 'teamB'; os_='teamB' if ms=='teamA' else 'teamA'
    sub={t['team']:int(t['submittedGems']) for t in j['teams']}
    def tot(metric,team,r):
        return sum(at(t['runs'],r) for t in j['championTimelines'] if t['metric']==metric and t['owner'].get('team')==team)
    d=dict(id=m['matchId'],t=m['createdAt'],era='v50' if m['createdAt']>='2026-10-28T13:58' else 'old',opp=op['name'],rank=L[op['teamId']][0],map=m['map'],side=me['side'],
      res=me['result'],end=m['endReason'],rounds=j['match']['roundsCompleted'],bu=sub[ms],bo=sub[os_],draft_o=op['draftPicks'],draft_u=me['draftPicks'])
    for r in (100,200,400,800):
        for k,mt in (('g','earnedGold'),('d','deaths'),('k','kills'),('c','collectedGems')):
            d[f'{k}{r}']=(tot(mt,ms,r),tot(mt,os_,r))
    def first(metric,team):
        # first round the team total of a champion metric exceeds 0
        best=None
        for t in j['championTimelines']:
            if t['metric']==metric and t['owner'].get('team')==team:
                n=0
                for x in t['runs']:
                    if float(x['value'])>0:
                        best=n if best is None else min(best,n); break
                    n+=x['duration']
        return best
    def teamfirst(team):
        for t in j['teamTimelines']:
            if t['metric']=='submittedGems' and t['owner']==team:
                n=0
                for x in t['runs']:
                    if float(x['value'])>0: return n
                    n+=x['duration']
    d['fdep']=(teamfirst(ms),teamfirst(os_)); d['fdeath']=(first('deaths',ms),first('deaths',os_)); d['fkill']=(first('kills',ms),first('kills',os_))
    for r in (100,200,400): d[f's{r}']=(tot('spentGold',ms,r),tot('spentGold',os_,r))
    d['dn']=(sorted(c['name'] for c in j['roster']['champions'] if c['team']==ms),sorted(c['name'] for c in j['roster']['champions'] if c['team']==os_))
    d['faults']=j['diagnostics']['botFaults'][ms]
    rows.append(d)
json.dump(rows,open('rows.json','w'))
print(len(rows))
