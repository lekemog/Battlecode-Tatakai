import json,glob,collections,math
NM=['Ryth','Vesper','Vendetta','Cassi&Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','Heart']
M={}; rank={}
for f in glob.glob('/root/lab/an/ml/*.json'):
    d=json.load(open(f)); rank[d['team']['teamId']]=(d['team']['rank'],d['team']['name'],d['team']['rating'])
    for m in d['matches']:
        if m['status']=='finished' and all(t.get('draftPicks') for t in m['teams']): M[m['matchId']]=m
print('matches',len(M))
# top-10 drafts
top=[tid for tid,(r,n,_) in rank.items() if r<=10]
for tid in sorted(top,key=lambda t:rank[t][0]):
    c=collections.Counter(); w=collections.Counter(); n=0; wins=0
    for m in M.values():
        for t in m['teams']:
            if t['teamId']==tid and len(t['draftPicks'])==5:
                k=tuple(NM[p] for p in t['draftPicks']); c[k]+=1; w[k]+=t['result']=='win'
            if t['teamId']==tid: n+=1; wins+=t['result']=='win'
    print(f"#{rank[tid][0]} {rank[tid][1][:22]:22} {wins}/{n}", ' | '.join(f"{'-'.join(x[:4] for x in k)} {w[k]}/{v}" for k,v in c.most_common(3)))
# champion pick share and win rate in games between two ranked<=30 teams
P=collections.Counter(); W=collections.Counter(); T=0
for m in M.values():
    if not all(t['teamId'] in rank and rank[t['teamId']][0]<=30 for t in m['teams']): continue
    for t in m['teams']:
        T+=1
        for p in set(t['draftPicks']): P[p]+=1; W[p]+=t['result']=='win'
print('top30 vs top30 team-games',T)
for p,v in sorted(P.items(),key=lambda kv:-kv[1]): print(f"  {NM[p]:12} pick {v/T:.2f} win {W[p]/v:.3f}")
# us
us='9c16b699-cad2-453e-8042-dae23ff934d8'
vs=collections.defaultdict(lambda:[0,0]); tot=[0,0]
for m in M.values():
    ts=m['teams']
    if us not in [t['teamId'] for t in ts]: continue
    me=[t for t in ts if t['teamId']==us][0]; op=[t for t in ts if t['teamId']!=us][0]
    tot[0]+=1; tot[1]+=me['result']=='win'
    for p in set(op['draftPicks']): vs[NM[p]][0]+=1; vs[NM[p]][1]+=me['result']=='win'
    vs[('size',len(me['draftPicks']))][0]+=1; vs[('size',len(me['draftPicks']))][1]+=me['result']=='win'
print('Tatakai last',tot[0],'ranked: wins',tot[1])
for k,v in sorted(vs.items(),key=lambda kv:kv[1][1]/kv[1][0]): print('  vs',k,v[0],'games win',round(v[1]/v[0],2))
