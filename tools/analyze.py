import json,sys,collections
OURS=['Ren','Stellar','Cassi & Issac','Ryth']
def run(p):
    d=json.load(open(p))
    m=d['match']; dr=d['roster']['draft']
    A=[x['champion'] for x in dr if x['team']=='teamA']; B=[x['champion'] for x in dr if x['team']=='teamB']
    us='teamA' if A[:4]==OURS else 'teamB' if B[:4]==OURS else '?'
    if A[:4]==OURS and B[:4]==OURS:
        # decide by 5th pick logic
        us='teamA' if len(A)>4 and A[4]=='Marcella' else 'teamB' if len(B)>4 and B[4]=='Marcella' else 'both?'
    gems={t['team']:int(t['submittedGems']) for t in d['teams']}
    print('='*90); print(p.split('/')[-1][:40], f"{m['width']}x{m['height']} rounds={m['roundsStarted']} winner={m['outcome']} us={us}")
    print(' A:',A,'\n B:',B); print(' gems',gems, 'faults',d['diagnostics']['botFaults'])
    for t in d['teamTimelines']:
        s=0; pts=[]
        for r in t['runs']:
            pts.append((s,r['value'])); s+=r['duration']
        mark=[next((r for r,v in pts if int(v)>=g),None) for g in (100,250,500,750,1000)]
        print(f"  {t['owner']} first score r{pts[1][0] if len(pts)>1 else '-'}  reach100/250/500/750/1000: {mark}")
    print(f"  {'champ':10}{'team':6}{'K':>3}{'D':>3}{'A':>3}{'gold':>6}{'gemsCol':>8}{'sub':>6}{'lost?':>6}{'monDmg':>8}{'chDmg':>7}{'chTaken':>8}  items")
    ev=collections.defaultdict(list)
    for e in d['events']: ev[(e['owner'].get('id'),e['kind'])]=e['entries']
    for c,r in zip(d['champions'],d['roster']['champions']):
        mt=c['metrics']; items=','.join(f"{i['quantity']}x{i['item'].replace('Power ','P').replace('Emblem','Em').replace('Shard','Sh')}" for i in c['items'])
        lost=sum(int(x['value']) for x in ev[(r['id'],'gemLoss')])
        print(f"  {c['name']:10}{c['team'][-1]:6}{mt['kills']:>3}{mt['deaths']:>3}{mt['assists']:>3}{mt['earnedGold']:>6}{mt['collectedGems']:>8}{mt['submittedGems']:>6}{lost:>6}{mt['monsterDamageDone']:>8.0f}{mt['championDamageDone']:>7.0f}{mt['championDamageTaken']:>8.0f}  {items}")
    # deaths timeline
    names={r['id']:(r['name'],r['team'][-1]) for r in d['roster']['champions']}
    dl=[]
    for r in d['roster']['champions']:
        for x in ev[(r['id'],'death')]: dl.append((x['timestamp']['round'],names[r['id']],x['x'],x['y'],x['context']))
    print('  deaths:',sorted(dl))
    cl=[]
    for e in d['events']:
        if e['kind']=='gemCollection':
            for x in e['entries']: cl.append((x['timestamp']['round'],names[e['owner']['id']][1],int(x['value']),x['target']['id']))
    cl.sort()
    print('  captures (round,team,gems,group):',[(r,t,g,gid) for r,t,g,gid in cl])
    fe={k:sum(len(ev[(r['id'],'fuelExhausted')]) for r in d['roster']['champions'] if r['team']==k) for k in('teamA','teamB')}
    print('  fuelExhausted',fe)
for p in sys.argv[1:]: run(p)
