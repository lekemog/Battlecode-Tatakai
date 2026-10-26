"""Deep per-map comparison of US vs THEM over all decoded top-100 test games on a map.
usage: weakmap.py MAP [cycle-prefix-filter]"""
import json,os,sys,collections,statistics as st,re
MAP=sys.argv[1];FILT=sys.argv[2] if len(sys.argv)>2 else 'c'
sys.argv=['x'];exec(open('/home/claude/tools/replay/dataset.py').read().split('FEATS =')[0])
OUT='/home/claude/data/our_rep';idx=json.load(open(f'{OUT}/index.json'))
CH=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi']
M=load_map(MAP);W,H=M['W'],M['H']
A=collections.defaultdict(lambda:collections.defaultdict(list));ngames=0;wins=0
zoneD={'US':collections.Counter(),'TH':collections.Counter()};zoneT={'US':collections.Counter(),'TH':collections.Counter()}
init=collections.Counter();agg_hist=[];modes=collections.Counter();kill_by=collections.Counter()
for mid,v in idx.items():
    if v['map']!=MAP or not str(v.get('cycle','')).startswith(FILT):continue
    p=f'{OUT}/{mid}.json'
    if not os.path.exists(p):continue
    try:d=json.load(open(p))
    except Exception:continue
    R=d['rounds']
    if len(R)<100:continue
    ngames+=1;wins+=v['result']=='win'
    us=0 if v['side']=='a' else 1
    sp=[[(c['position']['x'],c['position']['y']) for c in R[2]['champions'] if c['team']==t and c.get('position')] for t in (0,1)]
    if not sp[0] or not sp[1]:sp=[[(c['position']['x'],c['position']['y']) for c in R[6]['champions'] if c['team']==t and c.get('position')] for t in (0,1)]
    DU=M['bfs'](sp[us]);DT=M['bfs'](sp[1-us])
    def zone(x,y):
        a,b=DU[x,y],DT[x,y]
        if a>=9999 or b>=9999:return 'unk'
        if a<=4:return 'home'
        if b<=4:return 'their_home'
        f=a/(a+b)
        return 'our_half' if f<.42 else 'middle' if f<=.58 else 'their_half'
    team_of={};typ={}
    for c in R[20]['champions']:team_of[c['entity']['index']]=c['team'];typ[c['entity']['index']]=CH[c['type']]
    pos_at={}
    # initiations: first champion-on-champion attack/cast of each engagement (gap >= 8 rounds)
    lastfight=-99
    pos_round=collections.defaultdict(dict)
    for t,r in enumerate(R):
        for c in r['champions']:
            if c.get('alive') and c.get('position'):pos_round[t][(c['position']['x'],c['position']['y'])]=c['team']
    for e in d['events']:
        rnd,kind,ak,ai,fx,fy,tx,ty=e[:8]
        if ak!=1 or kind not in(5,6) or rnd<10:continue
        tt=pos_round.get(rnd,{}).get((tx,ty))
        at=team_of.get(ai)
        if tt is None or at is None or tt==at:continue
        if rnd-lastfight>=8:
            init['US' if at==us else 'TH']+=1
        lastfight=rnd
    for w,S in ((us,'US'),(1-us,'TH')):
        pa={};pg={};deaths=0;banks=[];lostbag=0;caps=0;capg=0;ally5=[];alive=0;ft=None
        for t in range(10,len(R)):
            cs=[c for c in R[t]['champions'] if c['team']==w]
            P=[(c['position']['x'],c['position']['y']) for c in cs if c.get('alive') and c.get('position')]
            for c in cs:
                i=c['entity']['index'];g=c.get('gems') or 0
                if pa.get(i) and not c.get('alive'):
                    deaths+=1;lostbag+=pg.get(i,0)
                    pp=pos_at.get(i)
                    if pp:zoneD[S][zone(*pp)]+=1
                    if S=='US':kill_by[typ[i]]+=1
                if c.get('alive') and i in pg:
                    if g>pg[i]:caps+=1;capg+=g-pg[i]
                    if g<pg[i]:banks.append(pg[i])
                pa[i]=c.get('alive');pg[i]=g
                if c.get('alive') and c.get('position'):
                    x,y=c['position']['x'],c['position']['y'];pos_at[i]=(x,y);alive+=1
                    if t%5==0:
                        zoneT[S][zone(x,y)]+=1
                        ally5.append(sum(1 for q in P if q!=(x,y) and max(abs(q[0]-x),abs(q[1]-y))<=5))
            if ft is None and R[t]['submittedGems'][w]>0:ft=t
        T=lambda r:R[min(r,len(R)-1)]['submittedGems'][w]
        a=A[S];a['score@150'].append(T(150));a['score@300'].append(T(300));a['final'].append(R[-1]['submittedGems'][w])
        a['deaths'].append(deaths);a['bag_lost'].append(lostbag);a['gems_picked'].append(capg);a['banked'].append(sum(banks));a['n_banks'].append(len(banks))
        a['first_tribute'].append(ft or len(R));a['allies_within5'].append(st.mean(ally5) if ally5 else 0)
        a['maxhp@300'].append(st.mean(c['maxHealth'] for c in R[min(300,len(R)-1)]['champions'] if c['team']==w))
        a['gold@300'].append(sum(c.get('earnedGold',0) for c in R[min(300,len(R)-1)]['champions'] if c['team']==w))
    # our opponent model state from logs
    for f in (os.listdir(f'{OUT}/{mid}') if os.path.isdir(f'{OUT}/{mid}') else []):
        if not f.endswith('.stdout'):continue
        txt=open(f'{OUT}/{mid}/{f}','rb').read().replace(b'\x00',b'').decode('utf8','ignore')
        ag=[int(x) for x in re.findall(r' agg=(\d+)',txt)]
        if ag:agg_hist.append((max(ag),st.mean(ag)))
        modes['raid_on']+=('RAID on' in txt);modes['defensive(agg>=40) ever']+=bool(ag and max(ag)>=40)
print(f'== {MAP}: {ngames} top-100 games, {wins} wins')
for k in A['US']:
    u,t=A['US'][k],A['TH'][k]
    print(f'  {k:16} US {st.mean(u):8.1f}   THEM {st.mean(t):8.1f}')
for S in ('US','TH'):
    tot=sum(zoneT[S].values());dt=sum(zoneD[S].values())
    print(f'  {S} time by zone:',{z:round(n/tot,2) for z,n in zoneT[S].most_common()},' deaths by zone:',{z:round(n/max(1,dt),2) for z,n in zoneD[S].most_common()})
print('  fights initiated (first champion hit after 8 quiet rounds):',dict(init))
print('  our deaths by champion:',kill_by.most_common())
if agg_hist:print(f'  our opponent model: max aggression mean {st.mean(a for a,_ in agg_hist):.0f}, games reaching defensive posture {modes["defensive(agg>=40) ever"]}/{len(agg_hist)}, raid switched on {modes["raid_on"]}')
