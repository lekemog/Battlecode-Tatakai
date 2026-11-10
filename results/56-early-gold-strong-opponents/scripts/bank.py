import json,os,sys,collections
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
us=json.load(open('m_us.json'))
tot=[]
for g in sorted(us,key=lambda g:g['createdAt']):
    mid=g['matchId']
    if not os.path.exists(f'dec/{mid[:8]}.json'):continue
    me=[t for t in g['teams'] if t['name']=='Tatakai'][0];op=[t for t in g['teams'] if t is not me][0]
    s=json.load(open(f'sum/{mid}.json'));mt='teamA' if me['side']=='a' else 'teamB';ti=0 if mt=='teamA' else 1
    al=collections.Counter()
    subs=[]
    for e in s['events']:
        if e['kind']=='gemSubmission':
            for x in e['entries']: al[(x['x'],x['y'])]+=1
            if e['owner']['team']==mt: subs+= [(x['timestamp']['round'],e['owner']['id'],int(x['value'])) for x in e['entries']]
    altars=[p for p,c in al.items()]
    # cluster: keep tiles used >=2 or all
    d=json.load(open(f'dec/{mid[:8]}.json'));R=d['rounds']
    first={}
    for r in R:
        for c in r['champions']:
            if c['team']!=ti or not c['alive'] or 'position' not in c: continue
            k=c['entity']['index']
            if c['gems']>=25 and k not in first:
                p=(c['position']['x'],c['position']['y'])
                first[k]=(r['round'],c['gems'],min(cheb(p,a) for a in altars) if altars else -1)
    subs.sort()
    fs=subs[0][0] if subs else None
    row=sorted(first.values())[:1]
    print(mid[:8],op['name'][:6],g['map'][:18],'altars',len(altars),'first >=25 bag (round,gems,dist to altar):',row,'our first deposit',fs,'bag',subs[0][2] if subs else None)
