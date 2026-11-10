"""#55: summarise a paired batch (candidate vs base, both sides) from cambc --statistics JSON files.
usage: python3 -I tools/replay/pair55.py <cand> <base> <dir> [maps.txt]
Files are <map>_<teamA>_<teamB>.json. Prints wins and decided share, mean banked-gem margin, mean collected gems and
deaths per side, a binomial p-value, per-map results (cand wins / base wins over the two sides) and the maps with
a +-2 swing. With maps.txt only those maps (one per line) are counted."""
import json,glob,os,sys,math,collections
C,B,D=sys.argv[1:4]
only=set(open(sys.argv[4]).read().split()) if len(sys.argv)>4 else None
def last(tl,metric,team_name):
    tot=0
    for t in tl:
        if t['metric']==metric and t['owner'].get('team')==team_name:
            runs=t['runs']; tot+=int(float(runs[-1]['value'])) if runs else 0
    return tot
rows={}
for f in glob.glob(D+'/*.json'):
    t=os.path.basename(f)[:-5]
    if t=='manifest': continue
    try: j=json.load(open(f))
    except Exception: continue
    m,rest=t.split('_',1)
    if only is not None and m not in only: continue
    cs='teamA' if rest.startswith(C+'_') else 'teamB'; bs='teamB' if cs=='teamA' else 'teamA'
    sub={x['team']:int(x['submittedGems']) for x in j['teams']}
    oc=j['match']['outcome']
    tl=j['championTimelines']
    rows[t]=dict(m=m,side='A' if cs=='teamA' else 'B',w=oc==cs,l=oc==bs,mar=sub[cs]-sub[bs],rd=j['match']['roundsStarted'],
        colc=last(tl,'collectedGems',cs),colb=last(tl,'collectedGems',bs),dc=last(tl,'deaths',cs),db=last(tl,'deaths',bs),
        sc=sub[cs],sb=sub[bs],faults=j['diagnostics']['botFaults'])
n=len(rows); w=sum(r['w'] for r in rows.values()); l=sum(r['l'] for r in rows.values())
dec=w+l
p=sum(math.comb(dec,k) for k in range(w,dec+1))/2**dec if dec else 1.0
mean=lambda k:sum(r[k] for r in rows.values())/max(1,n)
print(f'PAIRED {C} vs {B}: games {n} cand wins {w} base wins {l} undecided {n-dec}  share {w/max(1,dec):.3f}  one-sided p {p:.3f}  mean margin {mean("mar"):+.0f}  banked {mean("sc"):.0f}/{mean("sb"):.0f}  collected {mean("colc"):.0f}/{mean("colb"):.0f}  deaths {mean("dc"):.1f}/{mean("db"):.1f}  rounds {mean("rd"):.0f}')
for side in 'AB':
    s=[r for r in rows.values() if r['side']==side]
    if s: print(f'  cand as {side}: games {len(s)} wins {sum(r["w"] for r in s)} margin {sum(r["mar"] for r in s)/len(s):+.0f}')
fault=[(t,r['faults']) for t,r in rows.items() if any(r['faults'].values())]
if fault: print('  bot faults:',fault[:6])
pm=collections.defaultdict(lambda:[0,0,0])
for r in rows.values():
    x=pm[r['m']]; x[0]+=r['w']; x[1]+=r['l']; x[2]+=r['mar']
print('  per map cand-wins/base-wins/margin-sum:',' '.join(f'{m}:{v[0]}-{v[1]}({v[2]:+d})' for m,v in sorted(pm.items())))
print('  maps with swing >= 2:',' '.join(f'{m}:{v[0]-v[1]:+d}' for m,v in sorted(pm.items()) if abs(v[0]-v[1])>=2))
