"""permap.py BOT [BOT..] -> wins/losses per map on the 21-map pool from the latest bench stats dirs."""
import json,glob,os,collections,sys
names={k:v['name'] for k,v in json.load(open('/home/claude/data/maps_index2.json')).items()}
def latest(bot):
    best={}
    for d in glob.glob(f'/home/claude/data/bench_{bot}_vs_*'):
        o=d.split('_vs_')[1].rsplit('_',1)[0]
        try:
            if 'n_' not in open(f'{d}/manifest.txt').read():continue
        except OSError:continue
        if o not in best or d>best[o]:best[o]=d
    return best
rows={}
for bot in sys.argv[1:]:
    L=collections.Counter()
    for o,d in latest(bot).items():
        for f in glob.glob(f'{d}/n_*.json'):
            m=os.path.basename(f)[:10];tag=os.path.basename(f)[11:-5]
            side='teamA' if tag.startswith(bot+'_') else 'teamB'
            r=json.load(open(f));L[names[m]]+=r['match']['outcome']!=side
    rows[bot]=L
print('losses per map (of 20)'.ljust(22),' '.join(b.rjust(6) for b in rows))
for m in sorted(names.values(),key=lambda m:-rows[sys.argv[1]][m]):
    print(m.ljust(22),' '.join(str(rows[b][m]).rjust(6) for b in rows))
print('TOTAL'.ljust(22),' '.join(str(sum(rows[b].values())).rjust(6) for b in rows))
