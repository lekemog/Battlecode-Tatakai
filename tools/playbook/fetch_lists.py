import json,subprocess,time,sys,os
lad=json.load(open('/root/lab/an/ladder.json'))['teams']
want=lad[:30]
uk=['BattleCats','Claudus Maximus','QS2isLaw','Rogue Lock Pickers','bentheboss','smurphy','DOOMSDAY','0xDEADBEEF','Tatakai']
want+=[t for t in lad if t['name'] in uk and t not in want]
for t in want:
    out=f"/root/lab/an/ml/{t['teamId']}.json"
    if os.path.exists(out): continue
    ms=[]; cur=None
    for page in range(2):
        cmd=['cambc','matches','list','--team',t['teamId'],'--kind','ranked','--limit','100','--json']+(['--cursor',cur] if cur else [])
        for attempt in range(4):
            r=subprocess.run(cmd,capture_output=True,text=True,cwd='/root/lab')
            try: d=json.loads(r.stdout); break
            except Exception: time.sleep(5*(attempt+1)); d=None
        if not d: break
        ms+=d['matches']; cur=d.get('nextCursor'); time.sleep(1)
        if not cur: break
    json.dump({'team':t,'matches':ms},open(out,'w')); print(t['rank'],t['name'],len(ms),flush=True)
