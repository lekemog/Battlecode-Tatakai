# Inputs: /root/rep/ids.txt (match side opponent map, from results/panel/t10b_240.json) and /root/rep/<match>.zip from `cambc matches download`; decoded JSON in /root/rep/dec/ from tools/replay/extract5.mjs.
import json,collections
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
P=lambda c:(c['position']['x'],c['position']['y'])
res=collections.Counter(); dmg=[]; rng_us=collections.Counter(); rng_th=collections.Counter()
fights=[]
for line in open('/root/rep/ids.txt'):
    mid,side,opp,m=line.split(); us=0 if side=='a' else 1
    d=json.load(open(f'/root/rep/dec/{mid}.json')); R=d['rounds']
    for c in R[5]['champions']:
        (rng_us if c['team']==us else rng_th)[c['attackRange']]+=1
    # segment fights: a 'fight' = rounds where any opposing champions within 4; group consecutive (gap<=5)
    prevhp={}; cur=None
    for r in R:
        al={(c['team'],c['entity']['index']):c for c in r['champions']}
        live=[c for c in r['champions'] if c['alive'] and 'position' in c]
        contact=[(a,b) for a in live for b in live if a['team']==us and b['team']!=us and cheb(P(a),P(b))<=4]
        if contact:
            if cur is None or r['round']-cur['last']>5:
                if cur: fights.append(cur)
                cur=dict(opp=opp,start=r['round'],last=r['round'],ud=0,td=0,usdmg=0,thdmg=0,nu=set(),nt=set())
            cur['last']=r['round']
            for a,b in contact: cur['nu'].add(a['entity']['index']); cur['nt'].add(b['entity']['index'])
        if cur and r['round']-cur['last']<=5:
            for k,c in al.items():
                ph=prevhp.get(k)
                if ph is not None:
                    if ph[0] and not c['alive']:
                        if k[0]==us: cur['ud']+=1
                        else: cur['td']+=1
                    if c['alive'] and ph[0] and c['health']<ph[1] and (k[1] in (cur['nu'] if k[0]==us else cur['nt'])):
                        if k[0]==us: cur['thdmg']+=ph[1]-c['health']
                        else: cur['usdmg']+=ph[1]-c['health']
        prevhp={k:(c['alive'],c['health']) for k,c in al.items()}
    if cur: fights.append(cur)
import pickle; pickle.dump(fights,open("/tmp/claude-0/fights.pkl","wb"))
print('attack ranges at r5: ours',dict(rng_us),' theirs',dict(rng_th))
F=[f for f in fights if f['ud']+f['td']>0]
print('fights',len(fights),'with a death',len(F))
for lab,cond in (('we had more champions',lambda f:len(f['nu'])>len(f['nt'])),('equal',lambda f:len(f['nu'])==len(f['nt'])),('they had more',lambda f:len(f['nu'])<len(f['nt']))):
    G=[f for f in F if cond(f)]
    if G: print(f"{lab:24} n={len(G):3} our deaths {sum(f['ud'] for f in G):3} theirs {sum(f['td'] for f in G):3}  hp damage taken us {sum(f['thdmg'] for f in G)/len(G):6.0f} dealt {sum(f['usdmg'] for f in G)/len(G):6.0f}")
E=[f for f in F if f['start']<=300]
print('fights with a death before r300:',len(E),'our deaths',sum(f['ud'] for f in E),'theirs',sum(f['td'] for f in E))
