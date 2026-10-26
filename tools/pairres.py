"""Paired results so far: pairres.py TAG botA botB -> wins, differing games, margins from summaries."""
import json,subprocess,time,sys
ME='9c16b699-cad2-453e-8042-dae23ff934d8';OUT='/home/claude/data/our_rep'
TAG=sys.argv[1];BOTS=sys.argv[2:]
res={}
for b in BOTS:
    try:G=json.load(open(f'{OUT}/cycle_{TAG}_{b}.json'))
    except Exception:continue
    for g in G:
        for t in range(6):
            r=subprocess.run(['cambc','match-groups','show',g['group'],'--json'],capture_output=True,text=True)
            if r.returncode==0:break
            time.sleep(15)
        else: continue
        for m in json.loads(r.stdout)['matches']:
            if m['status']!='finished':continue
            us=[t for t in m['teams'] if t['teamId']==ME][0];op=[t for t in m['teams'] if t['teamId']!=ME][0]
            res[(b,g['opp'],m['map'])]=(us.get('result'),m['matchId'],us,op)
json.dump({'|'.join(k):v[:2] for k,v in res.items()},open(f'{OUT}/{TAG}_results.json','w'))
common={(o,m) for (b,o,m) in res}
common={k for k in common if all((b,)+k in res for b in BOTS)}
for b in BOTS:print(b,'wins on common',sum(res[(b,)+k][0]=='win' for k in common),'/',len(common))
for k in sorted(common):
    r=[res[(b,)+k][0] for b in BOTS]
    if len(set(r))>1:print(k,r)
print('sample team record keys',list(res[next(iter(res))][2].keys()) if res else None)
