import json,sys,os,subprocess,time,statistics as st,collections
S=sys.argv[1];A=json.load(open(sys.argv[2]));B=json.load(open(sys.argv[3])) if len(sys.argv)>3 else []
def key(m):
    us=[t for t in m['teams'] if t['name']=='LionelMSISS'][0];th=[t for t in m['teams'] if t['name']!='LionelMSISS'][0]
    return (th['teamId'],m['map'],us['side'])
def st_(m):
    p=S+'/sum/%s.json'%m['matchId']
    for _ in range(5):
        if os.path.exists(p):break
        subprocess.run(['cambc','matches','summary',m['matchId'],'--json','-o',p],capture_output=True);time.sleep(2)
    d=json.load(open(p));us=[t for t in m['teams'] if t['name']=='LionelMSISS'][0];me='team'+us['side'].upper()
    ch=[c for c in d['champions'] if c['team']==me];M=lambda k:sum(float(c['metrics'][k]) for c in ch)
    return dict(win=us['result']=='win',gems=int([t for t in d['teams'] if t['team']==me][0]['submittedGems']),deaths=M('deaths'),kills=M('kills'),gold=M('earnedGold'),cdmg=M('championDamageDone'),map=m['map'],opp=[t for t in m['teams'] if t['name']!='LionelMSISS'][0]['name'])
a={key(m):st_(m) for m in A};b={key(m):st_(m) for m in B}
ks=[k for k in a if (not b) or k in b]
print('games',len(ks))
for f in ['win','gems','deaths','kills','gold','cdmg']:
    x=st.mean(a[k][f] for k in ks);y=st.mean(b[k][f] for k in ks) if b else float('nan')
    print(f'{f:7} A {x:8.2f}   B {y:8.2f}')
if b:
    print('B better gems in',sum(b[k]['gems']>a[k]['gems'] for k in ks),'flips W->L',sum(a[k]['win'] and not b[k]['win'] for k in ks),'L->W',sum(b[k]['win'] and not a[k]['win'] for k in ks))
pm=collections.defaultdict(lambda:[0,0,0])
for k in ks:
    pm[a[k]['map']][0]+=a[k]['win'];pm[a[k]['map']][2]+=1
    if b:pm[a[k]['map']][1]+=b[k]['win']
print('wins per map (A,B,of):',dict(pm))
po=collections.defaultdict(lambda:[0,0,0])
for k in ks:
    po[a[k]['opp']][0]+=a[k]['win'];po[a[k]['opp']][2]+=1
    if b:po[a[k]['opp']][1]+=b[k]['win']
print('wins per opp (A,B,of):',dict(po))
