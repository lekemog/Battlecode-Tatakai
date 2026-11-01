import json,sys,os,collections,statistics as st
sys.path.insert(0,'.')
from lib import *
want=json.load(open('want.json'))
us_all=json.load(open('m_us.json'))
T={"ha²t","Gamblr","Valenki","KratosMessi"}
recs=[]
for g in want:
    f=f"sum/{g['matchId']}.json"
    if not os.path.exists(f): continue
    try: s=load(g['matchId'])
    except Exception: continue
    for t in g['teams']:
        tm='team'+t['side'].upper()
        opp=[x for x in g['teams'] if x is not t][0]
        R=rich(s,tm)
        recs.append(dict(mid=g['matchId'],kind=g['kind'],map=g['map'],team=t['name'],opp=opp['name'],res=t['result'],side=t['side'],R=R,end=g['endReason'],rounds=s['match']['roundsCompleted']))
import pickle;pickle.dump(recs,open('recs.pkl','wb'))
print(len(recs))
