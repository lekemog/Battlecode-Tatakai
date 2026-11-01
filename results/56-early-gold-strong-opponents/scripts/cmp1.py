import pickle,statistics as st,collections
recs=pickle.load(open('recs.pkl','rb'))
def m(l): return round(st.mean(l),1) if l else None
def row(rs,label):
    E=lambda k:[r['R']['earned'][k] for r in rs]
    co=lambda k:[sum(1 for c in r['R']['coll'] if c[0]<=k) for r in rs]
    ki=lambda k:[sum(1 for c in r['R']['kills'] if c[0]<=k) for r in rs]
    de=lambda k:[sum(1 for c in r['R']['deaths'] if c[0]<=k) for r in rs]
    fb=[min([b[0] for b in r['R']['buys'] if not b[2].startswith('COMB')] or [999]) for r in rs]
    bank=[min([s[0] for s in r['R']['subs']] or [999]) for r in rs]
    nb=lambda k:[sum(1 for b in r['R']['buys'] if b[0]<=k and not b[2].startswith('COMB') and not b[2].endswith('*')) for r in rs]
    wins=sum(r['res']=='win' for r in rs)
    print(f"{label:28s} n={len(rs):3d} win={wins:3d} gold@100/200/300 {m(E(100))}/{m(E(200))}/{m(E(300))} coll@100/200 {m(co(100))}/{m(co(200))} kills@150/300 {m(ki(150))}/{m(ki(300))} deaths@150/300 {m(de(150))}/{m(de(300))} firstbuy {st.median(fb)} firstbank {st.median(bank)} items@100/200 {m(nb(100))}/{m(nb(200))}")
for n in ["ha²t","Gamblr","Valenki","KratosMessi"]:
    row([r for r in recs if r['team']==n],n+" (all)")
    row([r for r in recs if r['team']==n and r['opp']=="Tatakai"],n+" vs us")
    row([r for r in recs if r['team']=="Tatakai" and r['opp']==n],"us vs "+n)
row([r for r in recs if r['team']=="Tatakai"],"us (all in set)")
