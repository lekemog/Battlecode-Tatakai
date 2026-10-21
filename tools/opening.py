"""opening.py CACHE N -> first 150 rounds: camp kills by type per side, gold@50/100/150, first capture round, distance travelled from home."""
import json,os,zipfile,subprocess,tempfile,shutil,collections,statistics as st,sys
C=json.load(open(sys.argv[1]));N=int(sys.argv[2]) if len(sys.argv)>2 else 15
ids=[k for k in C if os.path.exists(f'/home/claude/data/fish/{k}.zip')][:N]
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
kills=collections.Counter();gold=collections.defaultdict(list);first_kill=[];far=[];g=0;ttypes=collections.Counter()
for mid in ids:
    v=C[mid];tmp=tempfile.mkdtemp(dir='/home/claude/data');zipfile.ZipFile(f'/home/claude/data/fish/{mid}.zip').extractall(tmp)
    subprocess.run(['node','/home/claude/tools/replay/extract3.mjs','/home/claude/data/vis3/assets',f'{tmp}/replay.repl26a',f'{tmp}/r.json'],capture_output=True)
    try:R=json.load(open(f'{tmp}/r.json'))['rounds']
    except Exception:shutil.rmtree(tmp);continue
    shutil.rmtree(tmp);g+=1
    rr=[r for r in R if r.get('round') is not None]
    s=0 if v['side']=='a' else 1
    byr={r['round']:r for r in R if isinstance(r.get('round'),int)}
    start=min(byr);home=None;fk=None
    for t in range(start,start+151):
        r=byr.get(t)
        if not r:continue
        if home is None:
            sp=[(c['position']['x'],c['position']['y']) for c in r['champions'] if c['team']==s and c.get('position')]
            if sp:home=(st.mean(p[0] for p in sp),st.mean(p[1] for p in sp))
        p=byr.get(t-1)
        if p:
            pc={c['entity']['index']:c for c in p['camps']}
            for c in r['camps']:
                q=pc.get(c['entity']['index'])
                if q and q['health']>0 and c['health']<=0 and q.get('position'):
                    al=[h for h in r['champions'] if h.get('alive') and h.get('position')]
                    if al:
                        b=min(al,key=lambda h:cheb((h['position']['x'],h['position']['y']),(q['position']['x'],q['position']['y'])))
                        if b['team']==s:
                            kills[q['type']]+=1
                            if fk is None:fk=t-start
        for k in (50,100,150):
            if t==start+k:gold[k].append(sum(c.get('earnedGold',0) for c in r['champions'] if c['team']==s))
        if t==start+150 and home:
            far.append(st.mean(cheb(home,(c['position']['x'],c['position']['y'])) for c in r['champions'] if c['team']==s and c.get('position')))
    if fk is not None:first_kill.append(fk)
tn=['wolf','elk','gem cl','gold cl','monolith','golem']
print(f'{sys.argv[1]}: {g} games | gold@50/100/150 {st.mean(gold[50]):.0f}/{st.mean(gold[100]):.0f}/{st.mean(gold[150]):.0f} | first camp kill r{st.median(first_kill)} | mean distance from home at r150 {st.mean(far):.1f}')
print('  camp kills in first 150 rounds per game:',', '.join(f'{tn[k]} {v/g:.1f}' for k,v in sorted(kills.items())))
