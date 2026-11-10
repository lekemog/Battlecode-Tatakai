import json,sys,os,statistics as st
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
us=json.load(open('m_us.json'))
def coh(mid,lo=30,hi=200):
    d=json.load(open(f'dec/{mid}.json'));R=d['rounds']
    res={0:[],1:[]};alone={0:[],1:[]};nn={0:[],1:[]};mid_d={0:[],1:[]}
    for r in R:
        if not(lo<=r['round']<=hi) or r['phase']!=1 and False: continue
        for t in (0,1):
            cs=[(c['position']['x'],c['position']['y']) for c in r['champions'] if c['team']==t and c['alive'] and 'position' in c]
            if len(cs)<3:continue
            cx=sum(p[0] for p in cs)/len(cs);cy=sum(p[1] for p in cs)/len(cs)
            res[t].append(st.mean(cheb(p,(cx,cy)) for p in cs))
            for i,p in enumerate(cs):
                d_=min(cheb(p,q) for j,q in enumerate(cs) if j!=i)
                nn[t].append(d_);alone[t].append(d_>7)
    return {t:(round(st.mean(res[t]),1) if res[t] else None,round(st.mean(nn[t]),1) if nn[t] else None,round(st.mean(alone[t]),2) if alone[t] else None) for t in (0,1)}
tot={'us':[], 'opp':[]}
for g in sorted(us,key=lambda g:g['createdAt']):
    mid=g['matchId'][:8]
    if not os.path.exists(f'dec/{mid}.json'):continue
    me=[t for t in g['teams'] if t['name']=='Tatakai'][0];op=[t for t in g['teams'] if t is not me][0]
    ot=0 if me['side']=='a' else 1
    c=coh(mid)
    print(mid,op['name'][:8],g['map'][:18],me['result'],'us(spread,nn,aloneFrac)',c[ot],'opp',c[1-ot])
    tot['us'].append(c[ot]);tot['opp'].append(c[1-ot])
for k in tot:
    v=[x for x in tot[k] if x[0] is not None]
    print(k,[round(st.mean(x[i] for x in v),2) for i in range(3)])
