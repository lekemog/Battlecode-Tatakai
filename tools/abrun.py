"""Run paired real-ladder scrims for several versions back to back.
usage: abrun.py SET_NAME bot1,bot2,... ; uses OPP list below. Last bot listed stays submitted unless --keep BOT."""
import json,subprocess,sys,time
OPPS=json.load(open(sys.argv[sys.argv.index('--opps')+1])) if '--opps' in sys.argv else []
A='/home/claude/tools/ab.py'
def run(c):return subprocess.run(c,capture_output=True,text=True,cwd='/home/claude/proj').stdout
setname=sys.argv[1];bots=sys.argv[2].split(',');keep=sys.argv[sys.argv.index('--keep')+1] if '--keep' in sys.argv else None
for b in bots:
    tag=f'{setname}_{b}'
    print(run(['cambc','submit',f'bots/{b}']).strip().split('\n')[-1],flush=True)
    time.sleep(50)
    queued=sum(1 for g in json.load(open('/home/claude/data/ab/groups.json')) if g['tag']==tag)
    have={g['opp'] for g in json.load(open('/home/claude/data/ab/groups.json')) if g['tag']==tag}
    for opp,maps in OPPS:
        if opp in have:continue
        for attempt in range(40):
            r=subprocess.run(['python3','-I',A,'create',tag,opp,maps],capture_output=True,text=True,cwd='/home/claude/proj')
            out=r.stdout.strip()
            if out.startswith('queued'):queued+=1;print(out,flush=True);break
            print('retry create',opp[:8],(r.stderr or '').strip().split('\n')[-1][:120],flush=True);time.sleep(90)
    while True:
        time.sleep(30)
        out=run(['python3','-I',A,'status',tag])
        last=[l for l in out.split('\n') if l.startswith('TOTAL')]
        if last and f'/{5*queued} finished' in last[0]:print(last[0],flush=True);break
if keep:print(run(['cambc','submit',f'bots/{keep}']).strip().split('\n')[-1])
