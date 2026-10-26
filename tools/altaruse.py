"""Tributes by altar and bag hold time per team from replay bundles. usage: altaruse.py MAP bundle.repl26a..."""
import json,sys,os,subprocess,zipfile,tempfile,collections
MAP=sys.argv[1];sys.argv,files=['x'],sys.argv[2:]
exec(open('/home/claude/tools/replay/dataset.py').read().split('FEATS =')[0])
alts=load_map(MAP).get('altars') or []
for f in files:
    td=tempfile.mkdtemp(dir='/tmp/claude-0/-home-claude/1a6e1a21-0974-5904-af74-73034a4d3e04/scratchpad')
    zipfile.ZipFile(f).extractall(td);js=td+'/r.json'
    subprocess.run(['node','/home/claude/tools/replay/extract.mjs','/home/claude/data/vis/assets',td+'/replay.repl26a',js],capture_output=True)
    R=json.load(open(js))['rounds'];C=[collections.Counter(),collections.Counter()];hold=[[],[]];pg={};since={}
    for t in range(10,len(R)):
        for c in R[t]['champions']:
            i=c['entity']['index'];g=c.get('gems') or 0;w=c['team']
            if c.get('alive') and c.get('position'):
                x,y=c['position']['x'],c['position']['y']
                if i in pg and g<pg[i]:
                    C[w][min(alts,key=lambda a:max(abs(a[0]-x),abs(a[1]-y)))]+=1
                    if i in since:hold[w].append(t-since[i])
                if g>0 and pg.get(i,0)==0:since[i]=t
            pg[i]=g
    print(os.path.basename(f)[:30],[(dict(C[w]),sorted(hold[w])[len(hold[w])//2] if hold[w] else None) for w in (0,1)])
    os.remove(js);os.remove(td+'/replay.repl26a')
