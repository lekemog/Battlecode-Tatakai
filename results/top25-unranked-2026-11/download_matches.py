import json,subprocess,time,os,sys
keep=json.load(open('keep.json')); keep.sort(key=lambda m:m['createdAt'],reverse=True)
kind=sys.argv[1]
for m in keep:
    i=m['matchId']
    if kind=='sum':
        p=f'sum/{i}.json'; cmd=['cambc','matches','summary',i,'--json','-o',p]
    else:
        p=f'rep/{i}.zip'; cmd=['cambc','matches','download',i,'-o',p]
        if i not in set(open('want.txt').read().split()): continue
    if os.path.exists(p) and os.path.getsize(p)>100: continue
    for a in range(10):
        r=subprocess.run(cmd,capture_output=True,text=True)
        if r.returncode==0: break
        s=r.stderr
        time.sleep(5*(a+1) if '429' in s or 'retry' in s.lower() else 3)
    time.sleep(1)
