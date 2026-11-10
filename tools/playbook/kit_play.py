import json,glob,collections,sys
NM={0:'Ryth',1:'Vesper',2:'Vendetta',3:'Cassi',4:'Issac',5:'Stellar',6:'Prism',7:'Marcella',8:'Willow',9:'Ren',10:'Varg',11:'Tavi',12:'Heart'}
want=set(sys.argv[2].split(','))
def ch(a,b): return max(abs(a['x']-b['x']),abs(a['y']-b['y']))
S=collections.defaultdict(collections.Counter)
for f in glob.glob(sys.argv[1]):
    d=json.load(open(f)); seen=set(); prev={}
    for r in d['rounds']:
        k=r['round']
        if k in seen or not r['champions']: continue
        seen.add(k)
        for c in r['champions']:
            n=NM.get(c['type']); 
            if n not in want or not c['alive']: continue
            s=S[n]; s['rounds']+=1
            en=[x for x in r['champions'] if x['team']!=c['team'] and x['alive']]
            al=[x for x in r['champions'] if x['team']==c['team'] and x is not c and x['alive']]
            de=min([ch(c['position'],x['position']) for x in en] or [99])
            key=(c['team'],c['entity']['index'],f)
            cd=c['cooldowns']
            if key in prev:
                for i in (0,1):
                    if prev[key][i]==0 and cd[i]>0:
                        s[f'cast{i}']+=1
                        if de<=6: s[f'cast{i}_pvp']+=1
            prev[key]=cd
            if de<=6:
                s['pvp']+=1; s['de_sum']+=de; s[f'd{min(de,6)}']+=1
                # allies closer to the nearest enemy than me (am I behind the line?)
                e0=min(en,key=lambda x:ch(c['position'],x['position']))
                s['allies_in_front']+=sum(1 for a in al if ch(a['position'],e0['position'])<de)
                s['allies_within3']+=sum(1 for a in al if ch(a['position'],c['position'])<=3)
                s['hpfrac']+=c['health']/max(1,c['maxHealth'])
            if k in (300,600): s[f'maxhp{k}']+=c['maxHealth']; s[f'foc{k}']+=c['focus']['effective']; s[f'str{k}']+=c['strength']['effective']; s[f'n{k}']+=1
for n,s in S.items():
    p=max(1,s['pvp']); R=s['rounds']
    print(f"{n:8} rounds {R:6} | enemy within 6: {p/R:.2f} of rounds, mean dist {s['de_sum']/p:.1f}, dist<=1 {s['d1']/p:.2f} 2 {s['d2']/p:.2f} 3 {s['d3']/p:.2f} 4 {s['d4']/p:.2f} 5-6 {(s['d5']+s['d6'])/p:.2f} | allies in front {s['allies_in_front']/p:.2f}, within 3 {s['allies_within3']/p:.2f}, hp {s['hpfrac']/p:.2f}")
    print(f"         casts per 100 rounds: slot0 {100*s['cast0']/R:.1f} (in fights {s['cast0_pvp']}/{s['cast0']}), slot1 {100*s['cast1']/R:.1f} (in fights {s['cast1_pvp']}/{s['cast1']}) | r300 hp {s['maxhp300']/max(1,s['n300']):.0f} foc {s['foc300']/max(1,s['n300']):.0f} str {s['str300']/max(1,s['n300']):.0f} | r600 hp {s['maxhp600']/max(1,s['n600']):.0f} foc {s['foc600']/max(1,s['n600']):.0f} str {s['str600']/max(1,s['n600']):.0f}")
