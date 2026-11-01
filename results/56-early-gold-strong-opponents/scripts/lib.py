import json,os,collections
CH={0:'ryth',1:'vesper_vale',2:'vendetta',3:'cassi_and_issac',4:'stellar',5:'prism',6:'marcella',7:'willow',8:'ren',9:'varg',10:'tavi',11:'heart_of_ruin'}
def tl_at(runs,r):
    t=0
    for x in runs:
        t+=x['duration']
        if r<t: return float(x['value'])
    return float(runs[-1]['value']) if runs else 0
def load(mid):
    return json.load(open(f"sum/{mid}.json"))
def team_stats(s,team,rounds=(100,200,300,400)):
    """team = 'teamA'/'teamB'"""
    ids=[c['id'] for c in s['roster']['champions'] if c['team']==team]
    names={c['id']:c['name'] for c in s['roster']['champions']}
    out={'draft':[c['name'] for c in s['roster']['champions'] if c['team']==team]}
    earn={r:0 for r in rounds}
    for t in s['championTimelines']:
        if t['owner']['id'] in ids and t['metric']=='earnedGold':
            for r in rounds: earn[r]+=tl_at(t['runs'],r)
    out['earned']=earn
    buys=[];camps=[];kills=[];deaths=[];subs=[]
    for e in s['events']:
        o=e['owner']
        if o.get('id') not in ids: continue
        for x in e['entries']:
            r=x['timestamp']['round']
            if e['kind']=='buyItem': buys.append((r,o['name'],x['target']['name'],int(x['amount'])))
            elif e['kind']=='buyConsumable': buys.append((r,o['name'],x['target']['name']+'*',int(x['amount'])))
            elif e['kind']=='itemCombination': buys.append((r,o['name'],'COMB '+x['target']['name'],0))
            elif e['kind']=='campClear': camps.append((r,o['name'],x['target']['id']))
            elif e['kind']=='kill': kills.append((r,o['name'],x['target'].get('name'),x['target'].get('team')))
            elif e['kind']=='death': deaths.append((r,o['name']))
            elif e['kind']=='gemSubmission': subs.append((r,o['name'],int(x['value'])))
    for l in (buys,camps,kills,deaths,subs): l.sort()
    out.update(buys=buys,camps=camps,kills=kills,deaths=deaths,subs=subs)
    out['submitted']=sum(int(t['submittedGems']) for t in s['teams'] if t['team']==team)
    return out

def rich(s,team):
    ids={c['id'] for c in s['roster']['champions'] if c['team']==team}
    base=team_stats(s,team,(50,100,150,200,300,400))
    coll=[];fights=[];wards=0
    for e in s['events']:
        o=e['owner']
        if o.get('id') not in ids: continue
        for x in e['entries']:
            r=x['timestamp']['round']
            if e['kind']=='gemCollection': coll.append((r,o['name'],int(x['value'])))
            if e['kind']=='wardPlacement': wards+=1
    coll.sort()
    base['coll']=coll
    base['wards']=wards
    return base
def cnt(l,r,idx=0): return sum(1 for x in l if x[idx]<=r)
