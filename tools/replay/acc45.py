"""#45 acceptance check: deposits, ring kills and breach logs in decoded 02the_pack ladder games.

usage: python3 -I tools/replay/acc45.py <dir>   (dir holds p<i>.json from extract4.mjs and p<i>/team-<side>.stdout)
Edit GAMES below for other matches."""
import json,sys,re,os
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
D=sys.argv[1]
GAMES=[('7e624263','#1 Intercontinental Fish','b'),('1d727b4c','#5 test4','a'),('c5cde853','#5 test4','a'),('022fb08e','#5 test4','a'),('221fc9a6','#5 test4','a'),('b5a96e8d','#5 test4','a')]
for i,(mid,opp,side) in enumerate(GAMES,1):
    us=1 if side=='b' else 0; th=1-us
    R=json.load(open(os.path.join(D,f'p{i}.json')))['rounds']
    ring={c['entity']['index']:(c['position']['x'],c['position']['y']) for c in R[2]['camps'] if c['group']==0}
    kills=[];seen=set()
    for r in R:
        for c in r['camps']:
            e=c['entity']['index']
            if e in ring and c['health']<=0 and e not in seen:
                seen.add(e)
                near=[ch['team'] for ch in r['champions'] if ch.get('alive') and 'position' in ch and cheb((ch['position']['x'],ch['position']['y']),ring[e])<=4]
                kills.append((r['round'],ring[e],'us' if us in near and th not in near else 'them' if th in near and us not in near else 'both' if near else '?'))
    deps=[];prev=[0,0]
    for r in R:
        sg=r['submittedGems']
        if sg[us]!=prev[us]: deps.append((r['round'],sg[us]-prev[us]))
        prev=list(sg)
    f=R[-1]; held=sum(c['gems'] for c in f['champions'] if c['team']==us)
    s=re.sub(r'\s+',' ',open(os.path.join(D,f'p{i}',f'team-{side}.stdout'),'rb').read().replace(b'\0',b'').decode('latin1'))
    br=re.findall(r'br45 r\d+',s); seal=len(re.findall('seal45 zone',s)); lv=len(re.findall('leave-ring',s))
    firstbr=br[0] if br else None
    ours=[k for k in kills if k[2] in ('us','both')]
    print(f"p{i} {mid} vs {opp} side {side.upper()} rounds {len(R)}: banked us {f['submittedGems'][us]} them {f['submittedGems'][th]} | held at end {held} | deposits {len(deps)} first {deps[0] if deps else None} | ring kills total {len(kills)} by-us {len(ours)} first {kills[0] if kills else None} | seal45 {seal} br45 lines {len(br)} first {firstbr} leave-ring {lv}")
