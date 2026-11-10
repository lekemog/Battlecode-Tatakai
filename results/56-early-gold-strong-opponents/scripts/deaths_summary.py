"""Early deaths (round <= 300) of both sides in the decoded games: loneliness, numbers, who dies. Run from the work dir (m_us.json, dec/)."""
import json,sys,os,collections,statistics as st
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import deaths
us=json.load(open('m_us.json'))
agg={'US':[], 'OPP':[]};perop={};first=[];firstopp=[];vic=collections.Counter();opv=collections.Counter()
for g in sorted(us,key=lambda g:g['createdAt']):
    mid=g['matchId'][:8]
    if not os.path.exists(f'dec/{mid}.json'):continue
    me=[t for t in g['teams'] if t['name']=='Tatakai'][0];op=[t for t in g['teams'] if t is not me][0]
    ot=0 if me['side']=='a' else 1
    out,sp=deaths.run(mid,ot,300)
    print('==',mid,op['name'],g['map'],me['result'],'us',me['side'])
    for o in out:
        k='US' if o['team']==ot else 'OPP'
        agg[k].append(o);perop.setdefault((op['name'],k),[]).append(o);(vic if k=='US' else opv)[o['who']]+=1
        print(f"  {k:3s} r{o['r']:3d} {o['who']:8s} hp{o['hp']:.0f}/{o['maxhp']:.0f} gems{o['gems']:3d} dOwn{o['dist_own']:3d} dEn{o['dist_enemy']:3d} foes<=7:{[(a,b) for a,b,_ in o['near_e']]} friends<=7:{o['near_a']}")
    fu=[o['r'] for o in out if o['team']==ot];fo=[o['r'] for o in out if o['team']!=ot]
    first.append(min(fu) if fu else 999);firstopp.append(min(fo) if fo else 999)
def summ(l):
    n=len(l)
    if not n:return 'n=0'
    return (f"n={n} alone={sum(1 for o in l if not o['near_a'])/n:.2f} foes>=2={sum(1 for o in l if len(o['near_e'])>=2)/n:.2f} "
            f"outnumbered(by2+)={sum(1 for o in l if len(o['near_e'])>len(o['near_a'])+1)/n:.2f} deaths<=r100={sum(1 for o in l if o['r']<=100)} "
            f"mean dist to nearer spawn={sum(min(o['dist_own'],o['dist_enemy']) for o in l)/n:.1f}")
print('\nSUMMARY (alone = no ally within 7 tiles one round before; foes = enemy champions within 7)')
for k in agg: print(k,summ(agg[k]))
for k,v in sorted(perop.items()): print(k,summ(v))
print('our deaths by champion',dict(vic));print('their deaths by champion',dict(opv))
print('median first death: us',st.median(first),'them',st.median(firstopp),'; ours first in',sum(1 for a,b in zip(first,firstopp) if a<b),'of',len(first))
