"""Calibrate fight evaluation on real top-100 replays: at every round where champions of both teams are
within 5 of each other, compute OUR-side vs THEIR-side power under two formulas and check which predicts
who loses more champions in the next 15 rounds. usage: fightcal.py"""
import json,os,collections,random
OUT='/home/claude/data/our_rep';idx=json.load(open(f'{OUT}/index.json'))
def auc(pairs):
    pos=[s for s,y in pairs if y==1];neg=[s for s,y in pairs if y==0]
    if not pos or not neg:return None
    random.seed(1);P=random.sample(pos,min(3000,len(pos)));N=random.sample(neg,min(3000,len(neg)))
    w=sum((p>n)+.5*(p==n) for p in P for n in N);return w/(len(P)*len(N))
F={'strength only':lambda c:c['strength']['effective'],'strength+0.5*focus':lambda c:c['strength']['effective']+.5*c['focus']['effective'],'strength+focus':lambda c:c['strength']['effective']+c['focus']['effective']}
data={k:[] for k in F};ng=0
for mid,v in idx.items():
    c=str(v.get('cycle',''))
    if not (c.startswith('c4') or c.startswith('c5') or c.startswith('c6') or c.startswith('c8w') or c.startswith('d1')) or not os.path.exists(f'{OUT}/{mid}.json'):continue
    try:R=json.load(open(f'{OUT}/{mid}.json'))['rounds']
    except Exception:continue
    ng+=1
    if ng>140:break
    us=0 if v['side']=='a' else 1;last=-99
    for t in range(20,len(R)-16,3):
        cs=[c for c in R[t]['champions'] if c.get('alive') and c.get('position')]
        U=[c for c in cs if c['team']==us];T=[c for c in cs if c['team']!=us]
        pairs=[(a,b) for a in U for b in T if max(abs(a['position']['x']-b['position']['x']),abs(a['position']['y']-b['position']['y']))<=4]
        if not pairs or t-last<6:continue
        last=t
        ua={id(a):a for a,b in pairs};ta={id(b):b for a,b in pairs}
        # include allies within 5 of any engaged champion
        cx=[a['position'] for a in ua.values()]+[b['position'] for b in ta.values()]
        inr=lambda c:any(max(abs(c['position']['x']-p['x']),abs(c['position']['y']-p['y']))<=5 for p in cx)
        UU=[c for c in U if inr(c)];TT=[c for c in T if inr(c)]
        ids={c['entity']['index'] for c in UU+TT}
        later={c['entity']['index']:c.get('alive') for c in R[t+15]['champions']}
        dU=sum(1 for c in UU if not later.get(c['entity']['index'],True));dT=sum(1 for c in TT if not later.get(c['entity']['index'],True))
        if dU==dT:continue
        y=1 if dT>dU else 0   # we won the exchange
        for k,f in F.items():
            o=sum(f(c)*c['health'] for c in UU);th=sum(f(c)*c['health'] for c in TT)
            data[k].append((o/(o+th),y))
print('games',ng,'decisive engagements',len(data['strength only']))
for k in F:print(f'  {k:20} AUC {auc(data[k]):.3f}')
# calibration of the old formula: when old ratio >=1.5 (we think we win clearly), how often did we win?
for k in F:
    hi=[y for s,y in data[k] if s>=.6];print(f'  {k:20} when we look >=1.5x stronger: won {sum(hi)}/{len(hi)} = {sum(hi)/max(1,len(hi)):.0%}')
print('win rate by power share (strength+0.5*focus); share .5 = equal, ratio r -> share r/(1+r)')
B=collections.defaultdict(list)
for s,y in data['strength+0.5*focus']:B[min(9,int(s*10))].append(y)
for b in sorted(B):print(f'  share {b/10:.1f}-{(b+1)/10:.1f} (ratio {b/10/(1-b/10+1e-9):.2f}-{(b+1)/10/(1-(b+1)/10+1e-9):.2f}): n {len(B[b])} won {sum(B[b])/len(B[b]):.0%}')
