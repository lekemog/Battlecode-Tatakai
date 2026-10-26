"""Per-map view of the latest bench A vs B: benchmaps.py A B"""
import json,glob,sys;sys.argv,args=['x'],sys.argv[1:]
exec(open('/home/claude/tools/replay/dataset.py').read().split('def load_map')[0])
inv={v:k for k,v in HASH.items()};A,B=args
d=sorted(glob.glob(f'/home/claude/data/bench_{A}_vs_{B}_*'))[-1]
tot=0
for p in sorted(glob.glob(d+'/*.json')):
    t=p.split('/')[-1][:-5];j=json.load(open(p));g={x['team']:int(x['submittedGems']) for x in j['teams']}
    first=t[11:].split('_')[0];sa='teamA' if first==A else 'teamB';sb='teamB' if sa=='teamA' else 'teamA'
    won=j['match']['outcome']==sa;tot+=won
    print(f'{inv.get(t[2:6],t[2:6]):12} {A} as {sa[-1]}: {"WIN " if won else "loss"} {g[sa]:5}-{g[sb]:5}')
print('wins',tot)
