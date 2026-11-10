"""Per-family results from bench_stats.py output.
usage: python3 -I tools/lab/family_report.py BOT $BENCH_OUT mapfamilies.csv
For every family and opponent: games, wins, win rate, mean gem margin, mean deaths, mean banked gems (ours), zero-deposit games, round-2000 games."""
import json,glob,os,sys,collections
bot,d,fcsv=sys.argv[1:4]
fam={l.split(',')[0]:l.split(',')[1] for l in open(fcsv).read().split('\n')[1:] if l}
# map names may differ between hyphen/underscore forms
norm=lambda s:s.replace('_','-')
fam={norm(k):v for k,v in fam.items()}
S=collections.defaultdict(lambda:collections.defaultdict(list))
for f in glob.glob(d+'/bench_%s_vs_*/*.json'%bot):
    b=os.path.basename(f)[:-5]
    if b=='manifest' or '_' not in b: continue
    opp=os.path.basename(os.path.dirname(f)).split('_vs_')[1].rsplit('_',1)[0]
    try: j=json.load(open(f))
    except Exception: continue
    if 'agg' not in j: continue
    # <map>_<first>_<second>
    first_us = ('_%s_%s'%(bot,opp)) in b
    m=b[:-len('_%s_%s'%(bot,opp))] if first_us else b[:-len('_%s_%s'%(opp,bot))]
    us='teamA' if first_us else 'teamB';them='teamB' if first_us else 'teamA'
    g={t['team']:int(t['submittedGems']) for t in j['teams']}
    fm=fam.get(norm(m),'?')
    a=j['agg'].get(us,{})
    S[fm][opp].append(dict(win=j['match']['outcome']==us,margin=g[us]-g[them],deaths=a.get('deaths',0),bank=g[us],r2000=j['match']['roundsStarted']>=2000))
print(f'{"family":12} {"opponent":10} {"n":>3} {"win%":>5} {"margin":>7} {"deaths":>6} {"banked":>6} {"zero-dep":>8} {"r2000":>5}')
for fm in sorted(S):
    for opp in sorted(S[fm]):
        x=S[fm][opp];n=len(x)
        print(f'{fm:12} {opp:10} {n:3} {100*sum(r["win"] for r in x)/n:5.0f} {sum(r["margin"] for r in x)/n:+7.0f} {sum(r["deaths"] for r in x)/n:6.1f} {sum(r["bank"] for r in x)/n:6.0f} {sum(r["bank"]==0 for r in x):8} {sum(r["r2000"] for r in x):5}')
