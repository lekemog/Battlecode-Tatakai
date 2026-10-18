"""Report on data/topfights.json (top-10 vs top-10 engagements)."""
import json,collections,random
S=json.load(open('/home/claude/data/topfights.json'))
def auc(p):
    P=[s for s,y in p if y==1];N=[s for s,y in p if y==0]
    if not P or not N:return float('nan')
    random.seed(1);P=random.sample(P,min(3000,len(P)));N=random.sample(N,min(3000,len(N)))
    return sum((a>b)+.5*(a==b) for a in P for b in N)/(len(P)*len(N))
dec=[s for s in S if s['dA']!=s['dB']]
print(f"top-10 vs top-10: {len({s['g'] for s in S})} games, {len(S)} engagements, {len(dec)} decisive")
for k,n in (('s0','strength only'),('s5','strength+0.5*focus'),('s1','strength+focus')):
    print(f'  AUC {n:20} {auc([(s[k],1 if s["dB"]>s["dA"] else 0) for s in dec]):.3f}')
B=collections.defaultdict(list)
for s in dec:B[min(9,int(s['s5']*10))].append(1 if s['dB']>s['dA'] else 0)
print('  win rate for the side with power share x (strength+0.5*focus):')
for b in sorted(B):print(f'    share {b/10:.1f}-{(b+1)/10:.1f}: n {len(B[b]):4} win {sum(B[b])/len(B[b]):.0%}')
# how top teams pick fights: power share of the INITIATOR at engagement start
I=[]
for s in S:
    if s['ini'] is None:continue
    sh=s['s5'] if s['ini']==0 else 1-s['s5']
    won=None if s['dA']==s['dB'] else ((s['dB']>s['dA'])==(s['ini']==0))
    I.append((sh,won,(s['nA'] if s['ini']==0 else s['nB'])-(s['nB'] if s['ini']==0 else s['nA'])))
import statistics as st
print(f'  engagements with a clear initiator: {len(I)}; initiator power share median {st.median(x[0] for x in I):.2f}')
for lo,hi in ((0,.4),(.4,.5),(.5,.6),(.6,.7),(.7,1.01)):
    g=[x for x in I if lo<=x[0]<hi];d=[x for x in g if x[1] is not None]
    print(f'    initiator share {lo:.1f}-{hi:.1f}: {len(g)/len(I):.0%} of fights started, decisive win {sum(x[1] for x in d)/max(1,len(d)):.0%} (n {len(d)})')
nd=collections.Counter(x[2] for x in I);print('  initiator numbers advantage (their count - ours):',sorted(nd.items()))
