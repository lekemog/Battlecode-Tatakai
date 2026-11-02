"""Opening / fight / recall profile of one team in a decoded replay (tools/replay/extract4.mjs output).
usage: python3 -I open10.py <decoded.json> <team_index 0|1>   -> one JSON line
Fields: n (champions), spawn, cent{30,60,100}: (distance of the team centroid to own spawn, mean pairwise distance), contact (first round an
enemy champion is within 6 tiles of one of ours), fight300 (share of champion-rounds in r0-300 with an enemy within 6),
claims100/claims300 (groups claimed by the team by then), first_claim (round, camps), recalls_real (type-1 channel of >=4 rounds),
recalls_fake (type-1 channel of <=2 rounds), wards (distinct ward entities of the team), deaths."""
import json,sys,collections
d=json.load(open(sys.argv[1])); us=int(sys.argv[2]); R=d['rounds']
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
P=lambda c:(c['position']['x'],c['position']['y'])
mine=lambda r:[c for c in r['champions'] if c['team']==us and c['alive'] and 'position' in c]
r0=R[min(3,len(R)-1)]; m0=mine(r0)
sp=(sum(P(c)[0] for c in m0)/len(m0),sum(P(c)[1] for c in m0)/len(m0)) if m0 else (0,0)
size={c['entity']['index']:len(c) for c in []}
camps=collections.Counter(c['group'] for c in R[2]['camps'])
out=dict(n=len(m0),spawn=[round(sp[0]),round(sp[1])],W=d['size'] if 'size' in d else None)
cent={}
byr={r['round']:r for r in R}
for rd in (30,60,100):
    r=byr.get(rd)
    if not r: continue
    m=mine(r)
    if not m: continue
    cx=sum(P(c)[0] for c in m)/len(m); cy=sum(P(c)[1] for c in m)/len(m)
    pw=[cheb(P(a),P(b)) for i,a in enumerate(m) for b in m[i+1:]]
    cent[rd]=(round(cheb((cx,cy),sp)),round(sum(pw)/max(1,len(pw)),1))
out['cent']=cent
contact=None; inc=0; tot=0
for r in R:
    if r['round']>300: break
    en=[P(c) for c in r['champions'] if c['team']!=us and c['alive'] and 'position' in c]
    for c in mine(r):
        tot+=1
        if any(cheb(P(c),e)<=6 for e in en):
            inc+=1
            if contact is None: contact=r['round']
out['contact']=contact; out['fight300']=round(inc/max(1,tot),3)
cur={}; rr=collections.Counter(); wards=set(); deaths=0; alive={}
pg=None; claims=[]
for r in R:
    for c in r['champions']:
        if c['team']!=us: continue
        i=c['entity']['index']; t=c['channelType']; k=cur.get(i)
        if k and k[0]==t: cur[i]=(t,k[1]+1)
        else:
            if k and k[0]==1: rr['real' if k[1]>=4 else 'fake' if k[1]<=2 else 'mid']+=1
            cur[i]=(t,1)
        if alive.get(i,True) and not c['alive']: deaths+=1
        alive[i]=c['alive']
    for w in r.get('wards',[]):
        if w['team']==us: wards.add(w['entity']['index'])
    if pg:
        for i,g in enumerate(r['groups']):
            if g['state']==3 and pg[i][0]==2 and pg[i][1]==us: claims.append((r['round'],camps[i]))
    pg=[(g['state'],g['captureTeam']) for g in r['groups']]
out['claims100']=sum(1 for c in claims if c[0]<=100); out['claims300']=sum(1 for c in claims if c[0]<=300)
out['first_claim']=claims[0] if claims else None
out['recalls_real']=rr['real']; out['recalls_fake']=rr['fake']; out['recalls_mid']=rr['mid']; out['wards']=len(wards); out['deaths']=deaths
print(json.dumps(out))
