"""Join v18t decision traces (T lines) with replay deaths / lost bags. usage: traces.py CYCLE_PREFIX [MAP]"""
import json,os,re,sys,collections
PRE=sys.argv[1];MAPF=sys.argv[2] if len(sys.argv)>2 else None
OUT='/home/claude/data/our_rep';idx=json.load(open(f'{OUT}/index.json'))
CH=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi']
res=collections.defaultdict(lambda:collections.defaultdict(collections.Counter));games=collections.Counter();notes=collections.defaultdict(list)
for mid,v in idx.items():
    if not str(v.get('cycle','')).startswith(PRE) or (MAPF and v['map']!=MAPF):continue
    if not os.path.isdir(f'{OUT}/{mid}') or not os.path.exists(f'{OUT}/{mid}.json'):continue
    side='a' if v['side']=='a' else 'b'
    lf=f'{OUT}/{mid}/team-{side}.stdout'
    if not os.path.exists(lf):continue
    txt=open(lf,'rb').read().replace(b'\x00',b'').decode('utf8','ignore')
    T=collections.defaultdict(list)   # slot -> [(round, action, target, hp, gems, ne, e6, a5, flags, agg, ratio)]
    for m in re.finditer(r'^T (\d+) (\d+) (\S+) (-?\d+) (-?\d+) (\d+) (\d+) (\d+) (\d+) (\d\d) (\d+) (-?\d+)',txt,re.M):
        g=m.groups();T[int(g[1])].append((int(g[0]),g[2],int(g[3]),int(g[4]),int(g[5]),int(g[6]),int(g[7]),int(g[8]),g[9],int(g[10]),int(g[11])))
    if not T:continue
    try:R=json.load(open(f'{OUT}/{mid}.json'))['rounds']
    except Exception:continue
    us=0 if side=='a' else 1;games[v['map']]+=1
    ours=[c['entity']['index'] for c in R[20]['champions'] if c['team']==us];slot={e:k for k,e in enumerate(ours)}
    pa={};pg={}
    for t in range(10,len(R)):
        for c in R[t]['champions']:
            i=c['entity']['index']
            if c['team']!=us:continue
            g=c.get('gems') or 0
            if pa.get(i) and not c.get('alive'):
                k=slot.get(i);hist=[x for x in T.get(k,[]) if x[0]<=t][-4:]
                seq=' > '.join(x[1] for x in hist[-3:])
                last=hist[-1] if hist else None
                cat='bag' if pg.get(i,0)>=20 else 'nobag'
                res[v['map']][cat][seq]+=1
                if last and len(notes[v['map']])<6:notes[v['map']].append(f'{CH[c["type"]]} r{t} bag {pg.get(i,0)}: {seq} | last: hp {last[3]} near-enemy {last[5]} e6 {last[6]} a5 {last[7]} flags {last[8]} agg {last[9]} ratio {last[10]/100:.2f}')
            pa[i]=c.get('alive');pg[i]=g
for mp in res:
    print(f'== {mp} ({games[mp]} games) last 3 logged decisions before each of our deaths')
    for cat in ('bag','nobag'):
        tot=sum(res[mp][cat].values())
        print(f'  deaths {"carrying 20+" if cat=="bag" else "without a bag"}: {tot}')
        for s,n in res[mp][cat].most_common(6):print(f'     {n:3}  {s}')
    for x in notes[mp]:print('     e.g.',x)
