import json,os,collections,sys,statistics as st
sys.path.insert(0,'.')
from lib import tl_at
def gold_per_coll(s):
    """list of (round, team, champ id, group, gems, golddelta)"""
    tl={}
    for t in s['championTimelines']:
        if t['metric']=='earnedGold': tl[t['owner']['id']]=t
    out=[]
    for e in s['events']:
        if e['kind']!='gemCollection':continue
        o=e['owner']
        for x in e['entries']:
            r=x['timestamp']['round']
            if not isinstance(x.get('target'),dict):continue
            g=x['target']['id']
            run=tl[o['id']]['runs']
            d=tl_at(run,r)-tl_at(run,r-1)
            out.append((r,o['team'],o['id'],g,int(x['value']),d))
    return sorted(out)
if __name__=='__main__':
    us=json.load(open('m_us.json'))
    T=("ha²t","Gamblr","Valenki","KratosMessi")
    for g in sorted(us,key=lambda g:g['createdAt']):
        mid=g['matchId']
        if not any(t['name'] in T for t in g['teams']) or not os.path.exists(f'dec/{mid[:8]}.json'): continue
        s=json.load(open(f'sum/{mid}.json'))
        me=[t for t in g['teams'] if t['name']=='Tatakai'][0];op=[t for t in g['teams'] if t is not me][0]
        mt='team'+me['side'].upper()
        c=gold_per_coll(s)
        base=collections.defaultdict(list)
        for r,t,i,gr,gems,d in c: base[gr].append(d)
        gv={gr:st.median(v) for gr,v in base.items()}
        def tot(team,K): 
            L=[x for x in c if x[1]==team and x[0]<=K]
            return len(L),round(sum(x[5] for x in L))
        ot='teamB' if mt=='teamA' else 'teamA'
        print(mid[:8],op['name'][:6],g['map'][:16],me['result'],'us n/gold<=r200',tot(mt,200),'opp',tot(ot,200),'| us<=r100',tot(mt,100),'opp',tot(ot,100))
