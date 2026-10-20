"""permap3.py BOT [BOT..] -> losses per map (official map names) from the latest bench stats dirs on the 35-map pool."""
import json,glob,os,collections,sys
def latest(bot):
    best={}
    for d in glob.glob(f'/home/claude/data/bench_{bot}_vs_*'):
        o=d.split('_vs_')[1].rsplit('_',1)[0]
        try:
            if '01the-farm' not in open(f'{d}/manifest.txt').read():continue
        except OSError:continue
        if o not in best or d>best[o]:best[o]=d
    return best
rows={};games=collections.Counter()
for bot in sys.argv[1:]:
    L=collections.Counter()
    for o,d in latest(bot).items():
        for f in glob.glob(f'{d}/0*.json'):
            b=os.path.basename(f)[:-5];m=b.split('_')[0]
            side='teamA' if b[len(m)+1:].startswith(bot+'_') else 'teamB'
            r=json.load(open(f));L[m]+=r['match']['outcome']!=side
            if bot==sys.argv[1]:games[m]+=1
    rows[bot]=L
print('losses per map'.ljust(22),' '.join(b.rjust(6) for b in rows),' games')
for m in sorted(games,key=lambda m:-rows[sys.argv[1]][m]):
    print(m.ljust(22),' '.join(str(rows[b][m]).rjust(6) for b in rows),str(games[m]).rjust(6))
print('TOTAL'.ljust(22),' '.join(str(sum(rows[b].values())).rjust(6) for b in rows),str(sum(games.values())).rjust(6))
