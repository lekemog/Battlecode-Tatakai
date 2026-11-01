import pickle,statistics as st,collections,json
recs=pickle.load(open('recs.pkl','rb'))
want={g['matchId']:g for g in json.load(open('want.json'))}
CH={0:'ryth',1:'vesper',2:'vendetta',3:'cassi&issac',4:'stellar',5:'prism',6:'marcella',7:'willow',8:'ren',9:'varg',10:'tavi',11:'heart'}
def fam(n):
    if n.endswith('*'): return n[:-1]
    for k in('Treasure','Jungle','Capture','Monster','Durability','Bruiser','Power','Prospector','Home'):
        if n.startswith(k): return k
    return n.split()[0]
for team in ["ha²t","Gamblr","Valenki","KratosMessi","Tatakai"]:
    rs=[r for r in recs if r['team']==team]
    print("=====",team,len(rs))
    dr=collections.Counter()
    for r in rs:
        g=want[r['mid']]
        t=[t for t in g['teams'] if t['name']==team][0]
        dr[tuple(CH[p] for p in t['draftPicks'][:3])]+=1
    print(' draft first3:',dr.most_common(4))
    fc=collections.Counter();n=0
    for r in rs:
        for b in r['R']['buys']:
            if b[0]<=200 and not b[2].startswith('COMB'): fc[fam(b[2])]+=1
    print(' items<=r200 per game:',{k:round(v/len(rs),1) for k,v in fc.most_common(9)})
    first=collections.Counter()
    for r in rs:
        bb=[b for b in r['R']['buys'] if not b[2].startswith('COMB')]
        if bb: first[fam(bb[0][2])]+=1
    print(' first purchase family:',first.most_common(4))
    fcamp=[sorted(c[0] for c in r['R']['camps'])[:10] for r in rs if r['R']['camps']]
    print(' camp clears by r100/r200/r300 mean:',[round(st.mean(sum(1 for c in r['R']['camps'] if c[0]<=k) for r in rs),1) for k in(100,200,300)],' 10th clear round median',st.median([f[9] for f in fcamp if len(f)>=10] or [0]))
    print(' wards placed (all game) mean',round(st.mean(r['R']['wards'] for r in rs),1))
