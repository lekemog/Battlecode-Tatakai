"""#55: gem collection vs banking over time for both teams in one decoded replay (extract4.mjs output).
usage: python3 -I tools/replay/race55.py <decoded.json> <our_team_index 0=A 1=B> [bin=50]
Prints per bin: banked/collected/carried per team, alive champions, bag-hold rounds, rounds near an altar,
and the deposit list. Altar sites are inferred from where champions stood when submittedGems rose.
collected = cumulative positive growth of (banked + carried) per team (a death transfer counts for the killer)."""
import json,sys
path=sys.argv[1]; us=int(sys.argv[2]); BIN=int(sys.argv[3]) if len(sys.argv)>3 else 50
d=json.load(open(path)); R=d['rounds']
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
P=lambda c:(c['position']['x'],c['position']['y'])
# altar sites
prev=[0,0]; prevpos={}
sites=[]
for r in R:
    sg=r['submittedGems']
    for t in (0,1):
        if sg[t]!=prev[t]:
            for c in r['champions']:
                if c['team']==t and 'position' in c and prevpos.get(c['entity']['index']) is not None and c['alive'] is not None:
                    pass
            ps=[prevpos[i] for i in prevpos if prevpos[i][2]==t and prevpos[i][3]>0]
            if ps:
                # the champion whose bag dropped most
                best=max(ps,key=lambda p:p[3]); sites.append((r['round'],t,(best[0],best[1]),sg[t]-prev[t]))
    prev=list(sg)
    prevpos={c['entity']['index']:(c['position']['x'],c['position']['y'],c['team'],c['gems']) for c in r['champions'] if 'position' in c and c['alive']}
alt=[]
for _,t,p,_ in sites:
    if not any(cheb(p,q)<=2 for q in alt): alt.append(p)
print('altar-ish deposit sites',alt)
# camp positions
camps={c['entity']['index']:(c['position']['x'],c['position']['y'],c['group']) for c in R[2]['camps']}
prevtot=[0,0]; coll=[0,0]
bins={}
heldr=[0,0]; nearalt=[0,0]; aliver=[0,0]; ncs=[0,0]
for r in R:
    rd=r['round']
    carried=[0,0]; cnt=[0,0]
    for c in r['champions']:
        t=c['team']
        if c['alive'] and 'position' in c:
            cnt[t]+=1; carried[t]+=c['gems']
            if c['gems']>0: heldr[t]+=1
            if any(cheb(P(c),a)<=3 for a in alt): nearalt[t]+=1
    tot=[r['submittedGems'][t]+carried[t] for t in (0,1)]
    for t in (0,1):
        if tot[t]>prevtot[t]: coll[t]+=tot[t]-prevtot[t]
    prevtot=tot
    for t in (0,1): aliver[t]+=cnt[t]
    if rd%BIN==0 or rd==R[-1]['round']:
        bins[rd]=dict(b=list(r['submittedGems']),car=carried[:],col=coll[:],alive=cnt[:],held=heldr[:],near=nearalt[:],ar=aliver[:])
O,T=(us,1-us)
print('rd  | banked us/them | collected us/them | carried us/them | held-rounds(cum) | near-altar(cum) | champ-rounds(cum)')
for rd,x in sorted(bins.items()):
    print(f'{rd:4d} | {x["b"][O]:4d}/{x["b"][T]:4d} | {x["col"][O]:4d}/{x["col"][T]:4d} | {x["car"][O]:3d}/{x["car"][T]:3d} | {x["held"][O]:5d}/{x["held"][T]:5d} | {x["near"][O]:5d}/{x["near"][T]:5d} | {x["ar"][O]:5d}/{x["ar"][T]:5d}')
dep=[(a,t,w,b) for a,t,w,b in sites]
print('deposits us:',[(r,g) for r,t,_,g in dep if t==O])
print('deposits them:',[(r,g) for r,t,_,g in dep if t==T])
