"""Classify maps into strategy-stress families from tools/lab/mapfeatures.sh output.
usage: python3 -I tools/lab/mapfamilies.py $PROJ/mapfeatures.csv   -> prints map,family,tags and writes <csv dir>/mapfamilies.csv
Primary family (first match): gem-starved (<100 gems on the whole map), gem-only (gold <300), monolith (any monolith camp), elk-herd (8+ elk camps),
large (area > 5000), gold-rich (gold >= 2500), gold-poor (gold < 900), standard. Tags are the non-exclusive properties (size, altars, walls, ...)."""
import csv,sys,os
def fam(r):
    g=int(r['gold']);ge=int(r['gems']);mono=int(r['mono']);elk=int(r['elk']);area=int(r['w'])*int(r['h'])
    if ge<100: return 'gem-starved'
    if g<300: return 'gem-only'
    if mono>0: return 'monolith'
    if elk>=8: return 'elk-herd'
    if area>5000: return 'large'
    if g>=2500: return 'gold-rich'
    if g<900: return 'gold-poor'
    return 'standard'
def tags(r):
    t=[];area=int(r['w'])*int(r['h'])
    t.append('small' if area<1500 else 'big' if area>5000 else 'mid')
    t.append('altars%s'%r['altars']);
    if int(r['walls'])>250: t.append('walled')
    if int(r['golem'])>0: t.append('golems')
    if int(r['wolf'])>=15: t.append('wolf-packs')
    return '+'.join(t)
p=sys.argv[1];rows=list(csv.DictReader(open(p)))
out=[(r['map'],fam(r),tags(r)) for r in rows]
with open(os.path.join(os.path.dirname(os.path.abspath(p)),'mapfamilies.csv'),'w') as f:
    f.write('map,family,tags\n'); [f.write(','.join(x)+'\n') for x in out]
import collections
c=collections.Counter(x[1] for x in out)
for m,fm,t in out: print(f'{m:24} {fm:12} {t}')
print(dict(c))
