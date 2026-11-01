import json,collections
R=json.load(open('rows.json'))
print('ERA COUNTS')
for era in('v50','old'):
    X=[r for r in R if r['era']==era]; print(era,len(X),'wins',sum(r['res']=='win' for r in X))
def table(era):
    X=[r for r in R if r['era']==era]; by=collections.defaultdict(list)
    for r in X: by[(r['rank'],r['opp'])].append(r)
    print(f'| rank | opponent | {era} W-L | typical draft | deaths us/them r400 | earned gold us/them r200 | r800 | collected gems r400 | r800 | mean banked us/them (losses) |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for k,v in sorted(by.items()):
        n=len(v); w=sum(x['res']=='win' for x in v); L=[x for x in v if x['res']=='loss']
        f=lambda key,i:sum(x[key][i] for x in v)/n
        dr=collections.Counter(','.join(x['dn'][1]) for x in v).most_common(1)[0][0]
        bl=f'{sum(x["bu"] for x in L)/len(L):.0f}/{sum(x["bo"] for x in L)/len(L):.0f}' if L else '-'
        print(f'| {k[0]} | {k[1]} | {w}-{n-w} | {dr} | {f("d400",0):.1f}/{f("d400",1):.1f} | {f("g200",0):.0f}/{f("g200",1):.0f} | {f("g800",0):.0f}/{f("g800",1):.0f} | {f("c400",0):.0f}/{f("c400",1):.0f} | {f("c800",0):.0f}/{f("c800",1):.0f} | {bl} |')
table('v50'); print(); table('old')
