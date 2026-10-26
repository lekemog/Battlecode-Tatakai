"""channels.py CACHE N -> recall (1) / submit (2) / teleport (4) channel starts per game and the state when they start."""
import json,os,zipfile,subprocess,tempfile,shutil,collections,statistics as st,sys
C=json.load(open(sys.argv[1]));N=int(sys.argv[2]) if len(sys.argv)>2 else 12
ids=[k for k in C if os.path.exists(f'/home/claude/data/fish/{k}.zip')][:N]
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
starts=collections.defaultdict(list);done=collections.Counter()
for mid in ids:
    v=C[mid];tmp=tempfile.mkdtemp(dir='/home/claude/data');zipfile.ZipFile(f'/home/claude/data/fish/{mid}.zip').extractall(tmp)
    subprocess.run(['node','/home/claude/tools/replay/extract3.mjs','/home/claude/data/vis3/assets',f'{tmp}/replay.repl26a',f'{tmp}/r.json'],capture_output=True)
    try:R=json.load(open(f'{tmp}/r.json'))['rounds']
    except Exception:shutil.rmtree(tmp);continue
    shutil.rmtree(tmp)
    s=0 if v['side']=='a' else 1
    sp=[(c['position']['x'],c['position']['y']) for c in R[25]['champions'] if c['team']==s and c.get('position')]
    home=(st.mean(p[0] for p in sp),st.mean(p[1] for p in sp));prev={};prevpos={}
    for t in range(20,len(R)):
        for c in R[t]['champions']:
            if c['team']!=s:continue
            i=c['entity']['index'];ct=c.get('channelType') if c.get('alive') else 0
            if ct and prev.get(i)!=ct and c.get('position'):
                pos=(c['position']['x'],c['position']['y'])
                en=min([cheb(pos,(h['position']['x'],h['position']['y'])) for h in R[t]['champions'] if h['team']!=s and h.get('alive') and h.get('position')] or [99])
                starts[ct].append(dict(hp=c['health']/c['maxHealth'],gems=c.get('gems') or 0,gold=c.get('gold') or 0,home=cheb(pos,home),enemy=en))
            if prev.get(i)==1 and ct!=1 and c.get('alive') and c.get('position') and cheb((c['position']['x'],c['position']['y']),home)<=4:done[1]+=1
            prev[i]=ct
    done['games']+=1
g=max(1,done['games'])
print(f"{sys.argv[1]}: {g} games; recalls completed {done[1]/g:.1f}/game")
for ct,L in sorted(starts.items()):
    print(f' channel {ct}: {len(L)/g:.1f} starts/game',' '.join(f"{k} med {st.median(e[k] for e in L):.2f}" for k in ('hp','gems','gold','home','enemy')))
