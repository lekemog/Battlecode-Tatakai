"""Gauntlet: candidate vs the 7 bench opponents on the map pool, both sides, with per-game stats kept (see bench_stats.py).
usage: gauntlet.py CAND [opp1,opp2,...]   prints wins and margin per opponent and total."""
import subprocess,sys,os
C=sys.argv[1];O=(sys.argv[2] if len(sys.argv)>2 else 'x_daniel8,x_de41h4,h_mohnish,h_deysag,h_vatsal,h_photon,h_apex').split(',')
tw=tm=0
for o in O:
    r=subprocess.run(['python3','-I',os.path.join(os.path.dirname(os.path.abspath(__file__)),'bench_stats.py'),C,o],capture_output=True,text=True,env=dict(os.environ,JOBS=os.environ.get('JOBS','2')))
    line=[l for l in r.stdout.split('\n') if 'TOTAL' in l]
    print(o,line[-1] if line else r.stdout[-200:],flush=True)
    if line:
        p=line[-1].split();tw+=int(p[p.index('TOTAL')+1]);tm+=int(p[p.index('margin')+1])
print('GAUNTLET',C,'wins',tw,'/','(denominator is wrong; use per-opponent totals)','margin',tm)
