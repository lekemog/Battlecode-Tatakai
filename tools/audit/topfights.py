"""Fight study on top-vs-top replays (data/rep, both teams top-10): decode one at a time, extract every
engagement (champions of both teams within 4), record power share for team A under several formulas, who
initiated (first champion hit after 8 quiet rounds) and the outcome (more deaths in next 15 rounds), then
delete the decoded file. Writes samples to data/topfights.json. usage: topfights.py"""
import json,os,subprocess,collections
REP='/home/claude/data/rep';OUT='/home/claude/data/topfights.json';TMP='/home/claude/data/topdec'
os.makedirs(TMP,exist_ok=True)
meta=json.load(open(f'{REP}/meta.json'))
samples=json.load(open(OUT)) if os.path.exists(OUT) else []
done={s['g'] for s in samples}
CH=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi']
for mid,v in meta.items():
    ra,rb=v['teams']['a']['rank'] or 999,v['teams']['b']['rank'] or 999
    if max(ra,rb)>10 or mid in done:continue
    rp=f'{REP}/{mid}/replay.repl26a'
    if not os.path.exists(rp):continue
    js=f'{TMP}/{mid}.json'
    subprocess.run(['node','/home/claude/tools/replay/extract.mjs','/home/claude/data/vis/assets',rp,js],capture_output=True)
    try:d=json.load(open(js))
    except Exception:continue
    finally:
        if os.path.exists(js):os.remove(js)
    R=d['rounds'];team={c['entity']['index']:c['team'] for c in R[20]['champions']}
    hits=collections.defaultdict(list)
    posr={}
    for e in d['events']:
        if e[2]==1 and e[1] in(5,6):hits[e[0]].append(e)
    last=-99;lastfight=-99
    for t in range(20,len(R)-16,3):
        cs=[c for c in R[t]['champions'] if c.get('alive') and c.get('position')]
        A=[c for c in cs if c['team']==0];B=[c for c in cs if c['team']==1]
        pr=[(a,b) for a in A for b in B if max(abs(a['position']['x']-b['position']['x']),abs(a['position']['y']-b['position']['y']))<=4]
        if not pr or t-last<6:continue
        last=t
        cx=[a['position'] for a,b in pr]+[b['position'] for a,b in pr]
        inr=lambda c:any(max(abs(c['position']['x']-p['x']),abs(c['position']['y']-p['y']))<=5 for p in cx)
        AA=[c for c in A if inr(c)];BB=[c for c in B if inr(c)]
        later={c['entity']['index']:c.get('alive') for c in R[t+15]['champions']}
        dA=sum(1 for c in AA if not later.get(c['entity']['index'],True));dB=sum(1 for c in BB if not later.get(c['entity']['index'],True))
        # initiator: first cross-team hit in [t-6,t]
        pos={(c['position']['x'],c['position']['y']):c['team'] for c in cs}
        ini=None
        for tt in range(t-6,t+1):
            for e in hits.get(tt,[]):
                at=team.get(e[3]);tg=pos.get((e[6],e[7]))
                if at is not None and tg is not None and at!=tg:ini=at;break
            if ini is not None:break
        f=lambda C,k:sum((c['strength']['effective']+k*c['focus']['effective'])*c['health'] for c in C)
        samples.append({'g':mid,'t':t,'nA':len(AA),'nB':len(BB),'dA':dA,'dB':dB,'ini':ini,
            's0':f(AA,0)/max(1,f(AA,0)+f(BB,0)),'s5':f(AA,.5)/max(1,f(AA,.5)+f(BB,.5)),'s1':f(AA,1)/max(1,f(AA,1)+f(BB,1)),
            'hpA':sum(c['health'] for c in AA),'hpB':sum(c['health'] for c in BB),
            'gemsA':sum(c.get('gems') or 0 for c in AA),'gemsB':sum(c.get('gems') or 0 for c in BB)})
    json.dump(samples,open(OUT,'w'))
    print(mid[:8],v['map'],'samples',len(samples),flush=True)
