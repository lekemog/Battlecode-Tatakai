import sys,re
# tsum.py stdout : compress the bot's T trace into runs of (mode/why, target)
rows=[]
for l in open(sys.argv[1],errors='ignore'):
    m=re.search(r'T r(\d+) p(\d+),(\d+) hp(\d+) (\S+) e(\d) t(-?\d+) st(\d+) seen(\d) d(-?\d+) camps(\d+) allies(\d+) acts(\d)(\d)(\d)',l)
    if m: rows.append(m.groups())
runs=[]
for r in rows:
    key=(r[4],r[6])
    if runs and runs[-1]['key']==key: 
        u=runs[-1]; u['end']=int(r[0]); u['n']+=1; u['att']+=int(r[13]); u['mov']+=int(r[12]); u['hp1']=int(r[3]); u['p1']=(r[1],r[2])
    else: runs.append(dict(key=key,start=int(r[0]),end=int(r[0]),n=1,att=int(r[13]),mov=int(r[12]),hp0=int(r[3]),hp1=int(r[3]),p0=(r[1],r[2]),p1=(r[1],r[2])))
for u in runs: print(f"r{u['start']:4}-{u['end']:4} {u['key'][0]:22} t{u['key'][1]:>3} turns {u['n']:3} att {u['att']:3} mov {u['mov']:3} hp {u['hp0']}->{u['hp1']} {','.join(u['p0'])}->{','.join(u['p1'])}")
