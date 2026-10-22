"""Gauntlet: candidate vs a fixed set of diverse past bots on all pool maps, both sides.
usage: gauntlet.py CAND [opp1,opp2,...]   prints wins and margin per opponent and total."""
import subprocess,sys,os
C=sys.argv[1];O=(sys.argv[2] if len(sys.argv)>2 else 'v12m,v15e,v16g,v16o,v16w').split(',')
tw=tm=0
for o in O:
    r=subprocess.run(['python3','-I',os.path.join(os.path.dirname(os.path.abspath(__file__)),'bench.py'),C,o],capture_output=True,text=True,env=dict(os.environ,JOBS=os.environ.get('JOBS','2')))
    line=[l for l in r.stdout.split('\n') if 'TOTAL' in l]
    print(o,line[-1] if line else r.stdout[-200:],flush=True)
    if line:
        p=line[-1].split();tw+=int(p[p.index('TOTAL')+1]);tm+=int(p[p.index('margin')+1])
print('GAUNTLET',C,'wins',tw,'/',70*len(O),'margin',tm)
