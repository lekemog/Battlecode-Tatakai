import json,subprocess,os,re,time
us=json.load(open("m_us.json"))
T=("ha²t","Gamblr","Valenki","KratosMessi")
for g in us:
    if not any(t["name"] in T for t in g["teams"]): continue
    if g["createdAt"]<"2026-11-01T01:20": continue
    mid=g["matchId"];d=f"rep/{mid[:8]}"
    if os.path.exists(f"{d}/replay.repl26a"):continue
    z=f"rep/{mid[:8]}.zip"
    for t in range(6):
        r=subprocess.run(["cambc","matches","download",mid,"-o",z],capture_output=True,text=True)
        if os.path.exists(z):break
        m=re.search(r'retry after (\d+)',r.stderr+r.stdout);time.sleep(int(m.group(1))+1 if m else 3)
    os.makedirs(d,exist_ok=True)
    subprocess.run(["unzip","-o","-q",z,"-d",d])
