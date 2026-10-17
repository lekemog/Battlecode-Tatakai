"""Uncontested farming speed: bot vs a passive opponent on every pool map (both sides). Prints gems at r300/r400 and rounds to 1000."""
import json,os,subprocess,sys,time,statistics
PROJ='/home/claude/proj'
MAPS=os.environ.get('MAPS') or open('/home/claude/tools/pool.txt').read().strip()
MAPS=MAPS.split(',')
def gems_at(d,team,R):
    tl=[t for t in d['teamTimelines'] if t['owner']==team][0];s=0;v=0
    for r in tl['runs']:
        if s>R:break
        v=int(r['value']);s+=r['duration']
    return v
def run(bot,opp='starter-cpp'):
    out=f'/home/claude/data/speed_{bot}_{int(time.time()*1000)}';os.makedirs(out)
    rows=[]
    with open(f'{out}/manifest.txt','w') as f:
        for m in MAPS:
            for side in (0,1):
                a,b=(bot,opp) if side==0 else (opp,bot);tag=f'{m}_{side}'
                rows.append((m,side,tag))
                f.write(f'{PROJ}/bots/{a} {PROJ}/bots/{b} {PROJ}/maps/{m}.map26a {out}/{tag}.repl26a --statistics {out}/{tag}.json --json\n')
    subprocess.run(['cambc','run-batch',f'{out}/manifest.txt','--jobs',os.environ.get('JOBS','3'),'--release','--json','--timeout','900','--log-limit','0'],cwd=PROJ,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    res={}
    for m,side,tag in rows:
        p=f'{out}/{tag}.json'
        if not os.path.exists(p):continue
        d=json.load(open(p));team='teamA' if side==0 else 'teamB'
        g={t['team']:int(t['submittedGems']) for t in d['teams']}
        fin=d['match']['roundsStarted'] if g[team]>=1000 else 2000
        res.setdefault(m,[]).append((gems_at(d,team,300),gems_at(d,team,400),fin))
    return res
if __name__=='__main__':
    allr={}
    for bot in sys.argv[1:]:
        r=run(bot);allr[bot]=r
        flat=[x for v in r.values() for x in v]
        print(f'{bot:14} n={len(flat)} gems@300 {statistics.mean(x[0] for x in flat):.0f}  gems@400 {statistics.mean(x[1] for x in flat):.0f}  median finish {statistics.median(x[2] for x in flat):.0f}  mean finish {statistics.mean(x[2] for x in flat):.0f}',flush=True)
    if '-v' in os.environ.get('V',''):pass
    print('per map finish:')
    for m in MAPS:print(f'  {m}', '  '.join(f"{b}:{'/'.join(str(x[2]) for x in allr[b].get(m,[]))}" for b in allr))
