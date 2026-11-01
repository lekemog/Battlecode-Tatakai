"""Recall episodes per team from decoded replays: runs of consecutive rounds with channelType==1."""
import json,os,collections
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
us=json.load(open('m_us.json'))
res=collections.defaultdict(lambda:collections.Counter())
for g in us:
    mid=g['matchId'][:8]
    if not os.path.exists(f'dec/{mid}.json'):continue
    me=[t for t in g['teams'] if t['name']=='Tatakai'][0];op=[t for t in g['teams'] if t is not me][0]
    ti=0 if me['side']=='a' else 1
    d=json.load(open(f'dec/{mid}.json'))['rounds']
    R0=next(r for r in d if r['round']>=1 and r['champions'] and all('position' in c for c in r['champions']))
    sp={t:(sum(c['position']['x'] for c in R0['champions'] if c['team']==t)/max(1,sum(1 for c in R0['champions'] if c['team']==t)),sum(c['position']['y'] for c in R0['champions'] if c['team']==t)/max(1,sum(1 for c in R0['champions'] if c['team']==t))) for t in (0,1)}
    runs={}  # champ -> list of (round,timer,pos)
    for r in d:
        for c in r['champions']:
            k=(c['team'],c['entity']['index'])
            cur=runs.setdefault(k,{'run':[], 'done':[]})
            if c['alive'] and c['channelType']==1:
                cur['run'].append((r['round'],c['channelTimer'],(c['position']['x'],c['position']['y']) if 'position' in c else None))
            else:
                if cur['run']:
                    cur['done'].append((cur['run'],c))
                    cur['run']=[]
    for k,v in runs.items():
        name=op['name'] if k[0]!=ti else 'Tatakai'
        for run,after in v['done']:
            L=len(run); timers=[t for _,t,_ in run]
            const=len(set(timers))==1 and L>1
            home=after['alive'] and 'position' in after and cheb((after['position']['x'],after['position']['y']),sp[k[0]])<=6
            kind='len1' if L==1 else ('len2' if L==2 else ('len3-5' if L<=5 else 'len6+'))
            res[name][kind]+=1; res[name]['episodes']+=1
            if home: res[name][kind+'_home']+=1
            if const: res[name]['constant_timer']+=1
for n,c in res.items():
    e=c['episodes']
    print(n,'episodes',e,{k:v for k,v in sorted(c.items()) if k!='episodes'})
