# Inputs: /root/rep/ids.txt (match side opponent map, from results/panel/t10b_240.json) and /root/rep/<match>.zip from `cambc matches download`; decoded JSON in /root/rep/dec/ from tools/replay/extract5.mjs.
import json,collections,pickle
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
P=lambda c:(c['position']['x'],c['position']['y'])
NAMES=['Ryth','Vesper','Vendetta','Cassi&Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','Heart']
out=[]; first=[]
for line in open('/root/rep/ids.txt'):
    mid,side,opp,m=line.split(); us=0 if side=='a' else 1
    d=json.load(open(f'/root/rep/dec/{mid}.json')); R=d['rounds']; by={r['round']:r for r in R}
    def ch(r,team): return [c for c in r['champions'] if c['team']==team and c['alive'] and 'position' in c]
    r3=R[min(3,len(R)-1)]
    sp={t:tuple(sum(P(c)[k] for c in ch(r3,t))//max(1,len(ch(r3,t))) for k in (0,1)) for t in (0,1)}
    prev={}
    fdone=False
    for r in R:
        rd=r['round']
        if not fdone and rd>3:
            for a in ch(r,us):
                en=[e for e in ch(r,1-us) if cheb(P(e),P(a))<=4]
                if en:
                    c=P(a); nus=len([x for x in ch(r,us) if cheb(P(x),c)<=6]); nth=len([x for x in ch(r,1-us) if cheb(P(x),c)<=6])
                    f=cheb(c,sp[us])/(cheb(c,sp[us])+cheb(c,sp[1-us])+1e-9)
                    first.append(dict(opp=opp,map=m,r=rd,us=nus,them=nth,zone=f)); fdone=True; break
        for c in r['champions']:
            if c['team']!=us: continue
            i=c['entity']['index']
            if prev.get(i,True) and not c['alive'] and rd>1:
                hist=[]
                for k in range(12,0,-1):
                    q=by.get(rd-k)
                    if not q: continue
                    me=next((x for x in q['champions'] if x['team']==us and x['entity']['index']==i),None)
                    if not me or not me['alive'] or 'position' not in me: continue
                    p=P(me); en=ch(q,1-us); al=[x for x in ch(q,us) if x['entity']['index']!=i]
                    hist.append(dict(k=k,p=p,hp=me['health']/me['maxHealth'],home=cheb(p,sp[us]),
                        ne=min([cheb(P(e),p) for e in en] or [99]),e6=sum(cheb(P(e),p)<=6 for e in en),
                        a6=sum(cheb(P(x),p)<=6 for x in al),a10=sum(cheb(P(x),p)<=10 for x in al),
                        na=min([cheb(P(x),p) for x in al] or [99]),
                        rng=[e['attackRange'] for e in en if cheb(P(e),p)<=6]))
                if hist: out.append(dict(opp=opp,map=m,r=rd,type=NAMES[c['type']] if c['type']<12 else c['type'],h=hist,spd=None))
            prev[i]=c['alive']
pickle.dump((out,first),open('/tmp/claude-0/decdeaths.pkl','wb'))
print(len(out),len(first))
