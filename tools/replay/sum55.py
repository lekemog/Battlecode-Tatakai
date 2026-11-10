"""#55: one-line-per-game summary of a decoded replay for the gem-race study.
usage: python3 -I tools/replay/sum55.py <decoded.json> <our_team_index> [label]
Columns: gems collected (cumulative positive growth of banked+carried) at r200/r400/end, banked at end, groups claimed
(state 2 -> 3), camps claimed, champion-rounds in four activities (camp = within 3 of a camp that was in a group
not yet claimed that round; altar = within 3 of an inferred deposit site; carry = holding gems elsewhere; other),
deaths. All as us/them."""
import json,sys
from collections import Counter
path=sys.argv[1]; us=int(sys.argv[2]); lab=sys.argv[3] if len(sys.argv)>3 else path.split('/')[-1][:8]
d=json.load(open(path)); R=d['rounds']; O,T=us,1-us
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
camps=[(c['position']['x'],c['position']['y'],c['group']) for c in R[2]['camps']]
size=Counter(g for _,_,g in camps)
# altar sites
prev=[0,0]; prevc={}; alt=[]
for r in R:
    sg=r['submittedGems']
    for t in (0,1):
        if sg[t]!=prev[t]:
            ps=[v for v in prevc.values() if v[2]==t and v[3]>0]
            if ps:
                b=max(ps,key=lambda v:v[3]); p=(b[0],b[1])
                if not any(cheb(p,q)<=2 for q in alt): alt.append(p)
    prev=list(sg)
    prevc={c['entity']['index']:(c['position']['x'],c['position']['y'],c['team'],c['gems']) for c in r['champions'] if 'position' in c and c['alive']}
coll=[0,0]; pt=[0,0]; at={}; claims=[0,0]; camp_cl=[0,0]; pg=None
act=[Counter(),Counter()]; deaths=[0,0]; alive_prev={}; lost=[0,0]; bag_prev={}; ndep=[0,0]; sub_prev=[0,0]; maxbag=[0,0]
lastteam={}
for r in R:
    rd=r['round']; car=[0,0]
    claimed=set()
    for i,g in enumerate(r['groups']):
        if g['state']!=1: claimed.add(i)
    for c in r['champions']:
        t=c['team']; i=c['entity']['index']
        if c['alive'] and 'position' in c:
            car[t]+=c['gems']; p=(c['position']['x'],c['position']['y'])
            if any(cheb(p,a)<=3 for a in alt): a='altar'
            elif any(cheb(p,(x,y))<=3 and g not in claimed for x,y,g in camps): a='camp'
            elif c['gems']>0: a='carry'
            else: a='other'
            act[t][a]+=1
        if alive_prev.get(i,True) and not c['alive']:
            deaths[t]+=1; lost[t]+=bag_prev.get(i,0)
        if c['alive']: bag_prev[i]=c['gems']; maxbag[t]=max(maxbag[t],c['gems'])
        alive_prev[i]=c['alive']
    for t in (0,1):
        if r['submittedGems'][t]>sub_prev[t]: ndep[t]+=1
    sub_prev=list(r['submittedGems'])
    tot=[r['submittedGems'][t]+car[t] for t in (0,1)]
    for t in (0,1):
        if tot[t]>pt[t]: coll[t]+=tot[t]-pt[t]
    pt=tot
    if pg:
        for i,g in enumerate(r['groups']):
            if g['state']==3 and pg[i][0]==2 and pg[i][1] in (0,1):
                claims[pg[i][1]]+=1; camp_cl[pg[i][1]]+=size[i]
    pg=[(g['state'],g['captureTeam']) for g in r['groups']]
    if rd in (200,400): at[rd]=coll[:]
end=R[-1]['round']
f=lambda a:f'{a[O]:4d}/{a[T]:4d}'
ac=lambda t:' '.join(f'{k[0]}{act[t][k]*100//max(1,sum(act[t].values()))}' for k in ('camp','altar','carry','other'))
print(f'{lab} end{end:5d} coll200 {f(at.get(200,coll))} coll400 {f(at.get(400,coll))} collEnd {f(coll)} bank {f(R[-1]["submittedGems"])} groupsClaimed {f(claims)} campsClaimed {f(camp_cl)} deaths {f(deaths)} lostBag {f(lost)} deposits {f(ndep)} maxbag {f(maxbag)} | us% {ac(O)} | them% {ac(T)}')
