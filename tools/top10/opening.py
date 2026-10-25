import json,collections,statistics as st,os,sys
S=sys.argv[1];P=S+'/proj'
rows=json.load(open(S+'/unr_all.json'))
def load(m):
    G={};sp={}
    for l in open(P+'/mp3/%s.txt'%m):
        p=l.split()
        if p[0]=="GROUP" and len(p)==12 and p[10].count(",")==1 and all(x.isdigit() for x in p[10][1:].split(",")):
            G[int(p[1])]=dict(w=int(p[2][1:]),e=int(p[3][1:]),gc=int(p[4][2:]),oc=int(p[5][2:]),mo=int(p[6][2:]),go=int(p[7][2:]),gems=int(p[8][4:]),gold=int(p[9][4:]),c=tuple(map(int,p[10][1:].split(','))))
        if p[0]=="SPAWN" and len(p)==5:sp['A']=tuple(map(int,p[2].split(',')));sp['B']=tuple(map(int,p[4].split(',')))
    return G,sp
def kind(g):
    if g['mo']:return 'monolith'
    if g['go']:return 'golem'
    if g['e']:return 'elk'
    if g['w']:return 'wolf'
    return 'gemcl' if g['gems'] else 'goldcl'
cb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
agg={w:collections.defaultdict(list) for w in('us','them')}
kinds={w:collections.Counter() for w in('us','them')}
permap=collections.defaultdict(lambda:{'us':[], 'them':[]})
for m in rows:
    mp=m['map']
    if not os.path.exists(P+'/mp3/%s.txt'%mp):continue
    us=[t for t in m['teams'] if t['name']=='LionelMSISS'][0];th=[t for t in m['teams'] if t['name']!='LionelMSISS'][0]
    if th['name']=='BrendanBurgess':continue
    G,sp=load(mp)
    d=json.load(open(S+'/sum/%s.json'%m['matchId']))
    for who,t in (('us',us),('them',th)):
        tm='team'+t['side'].upper();home=sp[t['side'].upper()]
        buys=[];subs=[];clears=[]
        for e in d['events']:
            if e['owner'].get('team')!=tm:continue
            for x in e['entries']:
                r=x['timestamp']['round']
                if e['kind']=='buyItem':buys.append(r)
                if e['kind']=='gemSubmission':subs.append(r)
                if e['kind']=='campClear' and r<=150:clears.append((r,x['target']['id']))
        A=agg[who]
        A['clears75'].append(sum(r<=75 for r,_ in clears));A['clears150'].append(len(clears))
        A['first_clear'].append(min([r for r,_ in clears],default=150))
        A['first_buy'].append(min(buys,default=2000));A['first_bank'].append(min(subs,default=2000))
        A['dist'].extend(cb(G[g]['c'],home) for r,g in clears if g in G)
        for r,g in clears:
            if g in G:kinds[who][kind(G[g])]+=1
        permap[mp][who].append(sorted(clears)[:6])
n=len(agg['us']['clears150'])
print('games',n)
for k in ['clears75','clears150','first_clear','first_buy','first_bank','dist']:
    f=st.median if k.startswith('first') else st.mean
    print(f'{k:12} us {f(agg["us"][k]):6.1f}  them {f(agg["them"][k]):6.1f}')
for w in kinds:print(w,'clears by type r<=150 per game:',{k:round(v/n,2) for k,v in kinds[w].most_common()})
for mp in ['00lanes','00corners','00eight','01gold_rush']:
    G,_=load(mp)
    print('\n',mp)
    for who in('us','them'):
        for seq in permap[mp][who][:3]:print('  ',who,[(r,g,kind(G[g]) if g in G else '?') for r,g in seq])
