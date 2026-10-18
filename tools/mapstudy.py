"""Per-map study of our games: score race, deaths both sides, captures by group size, banking, positions.
usage: mapstudy.py MAP"""
import json,collections,statistics as st,sys,glob,os
MAP=sys.argv[1]
OUT='/home/claude/data/our_rep';idx=json.load(open(f'{OUT}/index.json'))
CH=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi']
rows=[]
for k,v in idx.items():
    if v['map']!=MAP:continue
    try:d=json.load(open(f'{OUT}/{k}.json'))
    except Exception:continue
    R=d['rounds']
    if len(R)<60:continue
    us=0 if v['side']=='a' else 1
    def at(t,tm):return R[min(t,len(R)-1)]['submittedGems'][tm]
    L=R[-1]
    deaths=[0,0];kills=[0,0]
    prev={c['entity']['index']:c.get('alive') for c in R[10]['champions']}
    caps=[collections.Counter(),collections.Counter()]
    pg={}
    first_trib=[None,None];bank_sizes=[[],[]]
    for t in range(11,len(R)):
        for c in R[t]['champions']:
            i=c['entity']['index'];w=0 if c['team']==us else 1
            if prev.get(i) and not c.get('alive'):deaths[w]+=1
            prev[i]=c.get('alive')
            g=c.get('gems') or 0
            if i in pg and g>pg[i] and c.get('alive'):caps[w][g-pg[i]]+=1
            if i in pg and g<pg[i] and c.get('alive'):bank_sizes[w].append(pg[i])
            pg[i]=g
        for w,tm in ((0,us),(1,1-us)):
            if first_trib[w] is None and R[t]['submittedGems'][tm]>0:first_trib[w]=t
    hp=[st.mean(c['maxHealth'] for c in R[min(300,len(R)-1)]['champions'] if (c['team']==us)==(w==0)) for w in (0,1)]
    draft=[sorted(CH[c['type']] for c in R[20]['champions'] if (c['team']==us)==(w==0)) for w in (0,1)]
    rows.append(dict(id=k,opp=v['opp'][:14],res=v['result'],cyc=v.get('cycle','ranked'),rounds=len(R),
        g200=(at(200,us),at(200,1-us)),g400=(at(400,us),at(400,1-us)),fin=(L['submittedGems'][us],L['submittedGems'][1-us]),
        deaths=deaths,first=first_trib,caps=[dict(sorted(c.items())) for c in caps],bank=[round(st.mean(b)) if b else 0 for b in bank_sizes],
        nbank=[len(b) for b in bank_sizes],hp=[round(h) for h in hp],draft=draft))
W=[r for r in rows if r['res']=='win'];Lo=[r for r in rows if r['res']!='win']
print(MAP,'games',len(rows),'wins',len(W))
for name,S in (('WINS',W),('LOSSES',Lo)):
    if not S:continue
    m=lambda f:round(st.mean(f(r) for r in S),1)
    print(f'{name}: n={len(S)} rounds {m(lambda r:r["rounds"])} | gems@200 us {m(lambda r:r["g200"][0])} them {m(lambda r:r["g200"][1])} | @400 us {m(lambda r:r["g400"][0])} them {m(lambda r:r["g400"][1])}'
          f' | deaths us {m(lambda r:r["deaths"][0])} them {m(lambda r:r["deaths"][1])} | first tribute us {m(lambda r:r["first"][0] or 2000)} them {m(lambda r:r["first"][1] or 2000)}'
          f' | bank size us {m(lambda r:r["bank"][0])} them {m(lambda r:r["bank"][1])} n {m(lambda r:r["nbank"][0])}/{m(lambda r:r["nbank"][1])} | maxHP@300 us {m(lambda r:r["hp"][0])} them {m(lambda r:r["hp"][1])}')
    cc=[collections.Counter(),collections.Counter()]
    for r in S:
        for w in (0,1):
            for a,b in r['caps'][w].items():cc[w][int(a)]+=b
    print('   pickups per game by size  us',{a:round(b/len(S),1) for a,b in sorted(cc[0].items()) if b/len(S)>=.3},' them',{a:round(b/len(S),1) for a,b in sorted(cc[1].items()) if b/len(S)>=.3})
    dr=collections.Counter(tuple(r['draft'][1]) for r in S);print('   opp drafts',dr.most_common(3))
json.dump(rows,open(f'{OUT}/mapstudy_{MAP}.json','w'))
