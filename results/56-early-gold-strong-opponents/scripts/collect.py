import subprocess,json,sys
teams={"ha2t":"ha²t","Gamblr":"Gamblr","Valenki":"Valenki","Kratos":"KratosMessi","us":"me"}
for k,v in teams.items():
    out=[];cur=None
    while len(out)<400:
        a=["cambc","matches","list","--team",v,"--limit","100","--json"]
        if cur:a+=["--cursor",cur]
        r=subprocess.run(a,capture_output=True,text=True,timeout=120)
        try:d=json.loads(r.stdout)
        except Exception as e: print(k,"err",r.stdout[:200],r.stderr[:200]);break
        out+=d["matches"];cur=d.get("nextCursor") or d.get("cursor")
        if not cur or not d["matches"]:break
    json.dump(out,open(f"m_{k}.json","w"))
    print(k,len(out),list(d.keys()))
