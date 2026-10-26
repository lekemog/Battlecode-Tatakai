"""How top teams play a map: decode top-team replays (data/rep) for MAP, summarise winner vs loser.
usage: howtheywin.py MAP"""
import json,os,subprocess,sys,statistics as st,collections,itertools
MAP=sys.argv[1];REP='/home/claude/data/rep';OUT='/home/claude/data/topdec'
CH=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi']
meta=json.load(open(f'{REP}/meta.json'))
agg={'W':collections.defaultdict(list),'L':collections.defaultdict(list)};drafts={'W':collections.Counter(),'L':collections.Counter()}
for mid,v in meta.items():
    if v['map']!=MAP:continue
    js=f'{OUT}/{mid}.json'
    if not os.path.exists(js):
        rp=f'{REP}/{mid}/replay.repl26a'
        if not os.path.exists(rp):continue
        subprocess.run(['node','/home/claude/tools/replay/extract.mjs','/home/claude/data/vis/assets',rp,js],capture_output=True)
    try:d=json.load(open(js))
    except Exception:continue
    R=d['rounds'];win=0 if v['teams']['a']['result']=='win' else 1
    ev=collections.defaultdict(set)
    for e in d['events']:
        if e[2]==1:ev[(e[0],e[3])].add(e[1])
    for tm in (0,1):
        S='W' if tm==win else 'L';A=agg[S]
        drafts[S][tuple(sorted(CH[c['type']][:3] for c in R[20]['champions'] if c['team']==tm))]+=1
        pg={};pa={};caps=collections.Counter();banks=[];deaths=0;spread=[];casts=0;att=0;alive=0;ft=None;enemyhalf=0
        for t in range(10,len(R)):
            cs=[c for c in R[t]['champions'] if c['team']==tm]
            for c in cs:
                i=c['entity']['index'];g=c.get('gems') or 0
                if pa.get(i) and not c.get('alive'):deaths+=1
                if c.get('alive') and i in pg:
                    if g>pg[i]:caps[g-pg[i]]+=1
                    if g<pg[i]:banks.append(pg[i])
                pa[i]=c.get('alive');pg[i]=g
                if c.get('alive'):
                    alive+=1;k=ev[(t,i)];casts+=6 in k;att+=5 in k
            if ft is None and R[t]['submittedGems'][tm]>0:ft=t
            if t%10==0:
                P=[(c['position']['x'],c['position']['y']) for c in cs if c.get('alive') and c.get('position')]
                if len(P)>1:spread.append(st.mean(max(abs(a[0]-b[0]),abs(a[1]-b[1])) for a,b in itertools.combinations(P,2)))
        T=min(300,len(R)-1)
        A['gems@300'].append(R[T]['submittedGems'][tm]);A['final'].append(R[-1]['submittedGems'][tm]);A['rounds'].append(len(R))
        A['deaths'].append(deaths);A['first_tribute'].append(ft or len(R));A['banks'].append(len(banks));A['bag'].append(st.mean(banks) if banks else 0)
        A['spread'].append(st.mean(spread) if spread else 0);A['cast/r'].append(casts/max(1,alive));A['attack/r'].append(att/max(1,alive))
        A['maxhp@300'].append(st.mean(c['maxHealth'] for c in R[T]['champions'] if c['team']==tm))
        for s,n in caps.items():A[f'pick{s}'].append(n)
print(MAP)
for S in ('W','L'):
    A=agg[S];n=len(A['final'])
    if not n:continue
    print(f' {"WINNERS" if S=="W" else "LOSERS "} n={n}: '+', '.join(f'{k} {st.mean(v):.1f}' for k,v in A.items() if not k.startswith('pick')))
    print('    pickups/game:',{k[4:]:round(sum(v)/n,1) for k,v in sorted(A.items(),key=lambda kv:int(kv[0][4:]) if kv[0].startswith('pick') else 0) if k.startswith('pick') and sum(v)/n>=.5})
    print('    drafts:',drafts[S].most_common(3))
