import subprocess,json,sys,time
kind=sys.argv[1]; out=[]; cur=None
while True:
    cmd=['cambc','matches','list','--team','me','--kind',kind,'--limit','100','--json']+(['--cursor',cur] if cur else [])
    for a in range(8):
        r=subprocess.run(cmd,capture_output=True,text=True)
        if r.returncode==0: break
        time.sleep(5*(a+1))
    else: print('fail',r.stderr[:200]); break
    j=json.loads(r.stdout); out+=j['matches']; cur=j.get('nextCursor') or j.get('cursor')
    print(kind,len(out),list(j.keys()),file=sys.stderr)
    if not cur or not j['matches']: break
    time.sleep(1)
json.dump(out,open(f'{kind}.json','w'))
