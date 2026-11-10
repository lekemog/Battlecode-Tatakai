import json,subprocess,os,re,time
T={"ha2t":"ha²t","Gamblr":"Gamblr","Valenki":"Valenki","Kratos":"KratosMessi"}
us=json.load(open("m_us.json"))
want=[]
for g in us:
    if any(t["name"] in T.values() for t in g["teams"]): want.append(g)
for k in T:
    ms=json.load(open(f"m_{k}.json"))
    want+= [g for g in ms if g["status"]=="finished"][:100]
seen=set();order=[]
for g in want:
    if g["matchId"] in seen: continue
    seen.add(g["matchId"]);order.append(g)
json.dump(order,open("want.json","w"))
print(len(order))
for g in order:
    f=f"sum/{g['matchId']}.json"
    if os.path.exists(f):continue
    for t in range(6):
        r=subprocess.run(["cambc","matches","summary",g["matchId"],"--json","-o",f],capture_output=True,text=True)
        if os.path.exists(f):break
        m=re.search(r'retry after (\d+)',r.stderr+r.stdout);time.sleep(int(m.group(1))+1 if m else 3)
