import json,sys
d=json.load(open(sys.argv[1])); team=int(sys.argv[2]); lo=int(sys.argv[3]); hi=int(sys.argv[4])
NM={0:'Ryth',1:'Vesp',2:'Vend',3:'Cassi',4:'Issac',5:'Stel',6:'Prism',7:'Marc',8:'Will',9:'Ren',10:'Varg',11:'Tavi',12:'Heart'}
seen=set()
for r in d['rounds']:
    k=r['round']
    if k in seen or k<lo or k>hi or not r['champions']: continue
    seen.add(k)
    cs=[c for c in r['champions'] if c['team']==team]
    awake=[(c['position']['x'],c['position']['y'],c['health'],c['group']) for c in r['camps'] if c.get('awake') and c['health']>0]
    def near(c):
        best=None
        for q in r['camps']:
            if q['health']<=0: continue
            dd=max(abs(q['position']['x']-c['position']['x']),abs(q['position']['y']-c['position']['y']))
            if best is None or dd<best[0]: best=(dd,q['group'],q['health'])
        return best
    print(k,' | '.join(f"{NM.get(c['type'],c['type'])[:4]} {c['position']['x']:2},{c['position']['y']:2} h{int(c['health']):4} g{c['gold']:3} n{near(c)}" for c in cs))
