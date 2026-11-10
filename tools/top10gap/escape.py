# Inputs: /root/rep/ids.txt (match side opponent map, from results/panel/t10b_240.json) and /root/rep/<match>.zip from `cambc matches download`; decoded JSON in /root/rep/dec/ from tools/replay/extract5.mjs.
import json,collections
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
P=lambda c:(c['position']['x'],c['position']['y'])
S={0:collections.Counter(),1:collections.Counter()}  # 0=us 1=them
for line in open('/root/rep/ids.txt'):
    mid,side,opp,m=line.split(); us=0 if side=='a' else 1
    d=json.load(open(f'/root/rep/dec/{mid}.json')); R=d['rounds']
    # episode: champion drops below 35% hp while an enemy champion within 5 -> did it die within 15 rounds? where was nearest enemy 3 rounds later?
    state={}
    for idx,r in enumerate(R):
        live=[c for c in r['champions'] if c['alive'] and 'position' in c]
        for c in r['champions']:
            k=(c['team'],c['entity']['index']); who=0 if c['team']==us else 1
            if not c['alive'] or 'position' not in c: continue
            low=c['health']<0.35*c['maxHealth']
            en=[e for e in live if e['team']!=c['team'] and cheb(P(e),P(c))<=5]
            if low and en and state.get(k,-99)<r['round']-20:
                state[k]=r['round']
                # outcome in next 15 rounds
                died=False; dist3=None; fled=None
                for q in R[idx+1:idx+16]:
                    me=next((x for x in q['champions'] if (x['team'],x['entity']['index'])==k),None)
                    if me and not me['alive']: died=True; break
                for q in R[idx+3:idx+4]:
                    me=next((x for x in q['champions'] if (x['team'],x['entity']['index'])==k),None)
                    if me and me['alive'] and 'position' in me:
                        ql=[e for e in q['champions'] if e['alive'] and 'position' in e and e['team']!=c['team']]
                        dist3=min([cheb(P(e),P(me)) for e in ql] or [99])
                        fled=me.get('channelType',0)
                S[who]['episodes']+=1; S[who]['died']+=died
                S[who]['already >=6 away 3 rounds later']+= (dist3 is not None and dist3>=6)
                S[who]['allies within 3 when low']+= sum(1 for a in live if a['team']==c['team'] and a is not c and cheb(P(a),P(c))<=3)>0
for w,n in ((0,'US'),(1,'THEM')):
    s=S[w]; e=max(1,s['episodes'])
    print(n, 'low-health-in-contact episodes',s['episodes'],' died within 15 rounds %.0f%%'%(100*s['died']/e),
          ' >=6 tiles from enemies 3 rounds later %.0f%%'%(100*s['already >=6 away 3 rounds later']/e),
          ' ally within 3 when low %.0f%%'%(100*s['allies within 3 when low']/e))
