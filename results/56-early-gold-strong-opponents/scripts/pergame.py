"""Markdown table: one row per decoded game vs the four teams. Run from the work dir."""
import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *
import deaths, groups
us=json.load(open('m_us.json'))
print('| id | opponent | map | our side | result | gold r200 us/opp | camp pickups r100 us/opp | deaths by r300 us/opp | first death us/opp | kills by r300 us/opp |')
print('|---|---|---|---|---|---|---|---|---|---|')
for g in sorted(us,key=lambda g:(g['teams'][0]['name'],g['createdAt'])):
    mid=g['matchId']
    if not os.path.exists(f'dec/{mid[:8]}.json'):continue
    me=[t for t in g['teams'] if t['name']=='Tatakai'][0];op=[t for t in g['teams'] if t is not me][0]
    mt='team'+me['side'].upper();ot='teamB' if mt=='teamA' else 'teamA'
    s=load(mid);A=team_stats(s,mt,(100,200,300));B=team_stats(s,ot,(100,200,300))
    c=groups.gold_per_coll(s)
    n100=lambda t:sum(1 for x in c if x[1]==t and x[0]<=100)
    tix=0 if me['side']=='a' else 1
    out,_=deaths.run(mid[:8],tix,300)
    du=[o['r'] for o in out if o['team']==tix];do=[o['r'] for o in out if o['team']!=tix]
    ku=sum(1 for k in A['kills'] if k[0]<=300);ko=sum(1 for k in B['kills'] if k[0]<=300)
    print(f"| {mid[:8]} | {op['name']} | {g['map']} | {me['side']} | {me['result']} | {int(A['earned'][200])}/{int(B['earned'][200])} | {n100(mt)}/{n100(ot)} | {len(du)}/{len(do)} | {min(du) if du else '-'}/{min(do) if do else '-'} | {ku}/{ko} |")
