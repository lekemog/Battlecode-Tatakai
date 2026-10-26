import json,collections,statistics as st,glob,os,sys
S=sys.argv[1]
meta={m['matchId']:m for m in json.load(open(S+'/unr_all.json'))}
cb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
def ctype(dp):return [dp] if dp<3 else ([3,4] if dp==3 else [dp+1])
M={w:collections.defaultdict(list) for w in('us','them')}
deathctx={w:collections.Counter() for w in('us','them')}
killhp={w:[] for w in('us','them')}
for f in glob.glob(S+'/rep/*.json'):
    mid=os.path.basename(f)[:-5]
    if mid not in meta:continue
    m=meta[mid];us=[t for t in m['teams'] if t['name']=='LionelMSISS'][0]
    R=json.load(open(f))['rounds']
    R=[r for r in R if r.get('champions')]
    if len(R)<50:continue
    types0={ch['type'] for ch in R[5]['champions'] if ch['team']==0}
    ourtypes={x for d in us['draftPicks'] for x in ctype(d)}
    our_team=0 if types0==ourtypes else 1
    # spawns from first alive positions
    sp={}
    for t in (0,1):
        ps=[(ch['position']['x'],ch['position']['y']) for ch in R[1]['champions'] if ch['team']==t and ch.get('position')]
        sp[t]=(sum(p[0] for p in ps)/len(ps),sum(p[1] for p in ps)/len(ps))
    prev=None
    for r in R[20:min(len(R),900)]:
        alive=[ch for ch in r['champions'] if ch['health']>0 and ch.get('position')]
        for ch in alive:
            t=ch['team'];w='us' if t==our_team else 'them';p=(ch['position']['x'],ch['position']['y'])
            mates=[a for a in alive if a['team']==t and a is not ch]
            foes=[a for a in alive if a['team']!=t]
            dm=min([cb(p,(a['position']['x'],a['position']['y'])) for a in mates],default=99)
            do,de=cb(p,sp[t]),cb(p,sp[1-t]);side=do/max(1,do+de)
            M[w]['alone6'].append(dm>6);M[w]['mates4'].append(sum(cb(p,(a['position']['x'],a['position']['y']))<=4 for a in mates))
            M[w]['home'].append(side<.4);M[w]['mid'].append(.4<=side<=.6);M[w]['enemyside'].append(side>.6);M[w]['atspawn'].append(do<=2)
            M[w]['low'].append(ch['health']<ch['maxHealth']*.3);M[w]['maxhp'].append(ch['maxHealth'])
            M[w]['foe_near'].append(any(cb(p,(a['position']['x'],a['position']['y']))<=6 for a in foes))
        if prev:
            pa={(c['team'],c['entity']['index']):c for c in prev['champions'] if c['health']>0 and c.get('position')}
            na={(c['team'],c['entity']['index']) for c in r['champions'] if c['health']>0}
            for k,c in pa.items():
                if k not in na:
                    t=k[0];w='us' if t==our_team else 'them';p=(c['position']['x'],c['position']['y'])
                    al=sum(1 for kk,a in pa.items() if kk[0]==t and kk!=k and cb(p,(a['position']['x'],a['position']['y']))<=5)
                    fo=sum(1 for kk,a in pa.items() if kk[0]!=t and cb(p,(a['position']['x'],a['position']['y']))<=5)
                    do,de=cb(p,sp[t]),cb(p,sp[1-t]);side=do/max(1,do+de)
                    deathctx[w][('alone' if al==0 else 'with_ally', 'foes%d'%min(fo,3), 'home' if side<.4 else 'mid' if side<=.6 else 'enemyside')]+=1
                    killhp[w].append(c['health']/c['maxHealth'])
        prev=r
for k in ['alone6','mates4','home','mid','enemyside','atspawn','low','foe_near','maxhp']:
    print(f'{k:10} us {st.mean(M["us"][k]):7.3f}  them {st.mean(M["them"][k]):7.3f}')
for w in('us','them'):
    n=sum(deathctx[w].values());print('\n',w,'deaths',n,'hp before death median',round(st.median(killhp[w]),2) if killhp[w] else None)
    a=collections.Counter();b=collections.Counter();c=collections.Counter()
    for (x,y,z),v in deathctx[w].items():a[x]+=v;b[y]+=v;c[z]+=v
    print('  ',dict(a),dict(b),dict(c))
