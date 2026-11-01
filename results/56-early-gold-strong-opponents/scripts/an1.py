import json,sys,collections
sys.path.insert(0,'.')
from lib import *
us=json.load(open('m_us.json'))
T=("ha²t","Gamblr","Valenki","KratosMessi")
rows=[]
for g in sorted(us,key=lambda g:g['createdAt']):
    o=[t for t in g['teams'] if t['name'] in T]
    if not o or g['createdAt']<'2026-11-01T01:20' and o[0]['name']!='KratosMessi': continue
    if not os.path.exists(f"sum/{g['matchId']}.json"): continue
    me=[t for t in g['teams'] if t['name']=='Tatakai'][0]; op=o[0]
    s=load(g['matchId'])
    tm=lambda t:'team'+t['side'].upper()
    A=team_stats(s,tm(op)); B=team_stats(s,tm(me))
    rows.append((g,me,op,A,B))
def fmt_buys(b,n=8):
    return ' '.join(f"r{r}:{c[:4]}:{i.replace('Treasure','T').replace('Durability','D').replace('Bruiser','B').replace('Shard of','s').replace('Emblem of','E').replace('Altar Lock','AL')}" for r,c,i,_ in b[:n])
for g,me,op,A,B in rows:
    print('=====',g['matchId'][:8],op['name'],g['map'],me['result'],'ourside',me['side'])
    for nm,X in(('OPP',A),('US ',B)):
        print(nm,'draft',[CH_ for CH_ in X['draft']],'earned',{k:int(v) for k,v in X['earned'].items()},'sub',X['submitted'])
        print('   buys',fmt_buys([b for b in X['buys'] if not b[2].startswith('COMB')],9))
        print('   camps',[(r,c[:4],gr) for r,c,gr in X['camps'][:8]])
        print('   kills',[(r,c[:4],t[:4]) for r,c,t,_ in X['kills'][:3]],'deaths',[(r,c[:4]) for r,c in X['deaths'][:3]])
