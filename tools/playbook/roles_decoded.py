import json,glob,collections,sys
NM={0:'Ryth',1:'Vesper',2:'Vendetta',3:'Cassi',4:'Issac',5:'Stellar',6:'Prism',7:'Marcella',8:'Willow',9:'Ren',10:'Varg',11:'Tavi',12:'Heart'}
def ch(a,b): return max(abs(a['x']-b['x']),abs(a['y']-b['y']))
S=collections.defaultdict(collections.Counter)
for f in glob.glob(sys.argv[1]):
    d=json.load(open(f)); seen=set()
    for r in d['rounds']:
        k=r['round']
        if k in seen or not r['champions'] or k<5 or k>int(sys.argv[2]) : continue
        seen.add(k)
        for c in r['champions']:
            if not c['alive'] or (len(sys.argv)>3 and c['team']!=int(sys.argv[3])): continue
            mates=[x for x in r['champions'] if x['team']==c['team'] and x is not c and x['alive']]
            if c['type'] in (3,4): mates=[x for x in mates if x['type'] not in (3,4)]  # pair partner not counted
            dm=min([ch(c['position'],x['position']) for x in mates] or [99])
            s=S[NM[c['type']]]; s['n']+=1; s['ally<=2']+=dm<=2; s['ally<=4']+=dm<=4; s['alone>8']+=dm>8
            # camps awake in whose range we are; are we the nearest champion of our team to it
            hit=0; tank=0
            for q in r['camps']:
                if q['health']>0 and q.get('awake') and q['strength']['effective']>0:
                    dq=ch(c['position'],q['position'])
                    if dq<=q['attackRange']:
                        hit=1
                        if all(ch(x['position'],q['position'])>=dq for x in mates): tank=1
            s['in_camp_range']+=hit; s['nearest_to_camp']+=tank
            s['gems']+=c['gems']; s['str']+=c['strength']['effective']; s['maxhp']+=c['maxHealth']
            if c['type']==3:
                i=[x for x in r['champions'] if x['team']==c['team'] and x['type']==4 and x['alive']]
                if i: s['pair<=2']+=ch(c['position'],i[0]['position'])<=2; s['pair<=4']+=ch(c['position'],i[0]['position'])<=4
print(f"{'':9} {'rounds':>6} ally<=2 ally<=4 alone>8 inCampRng tanking  gems   str  maxhp")
for n,s in sorted(S.items(),key=lambda kv:-kv[1]['n']):
    k=s['n']; print(f"{n:9} {k:6} {s['ally<=2']/k:7.2f} {s['ally<=4']/k:7.2f} {s['alone>8']/k:7.2f} {s['in_camp_range']/k:9.2f} {s['nearest_to_camp']/k:7.2f} {s['gems']/k:5.0f} {s['str']/k:5.0f} {s['maxhp']/k:6.0f}", (f"pair<=2 {s['pair<=2']/k:.2f} <=4 {s['pair<=4']/k:.2f}" if n=='Cassi' else ''))
