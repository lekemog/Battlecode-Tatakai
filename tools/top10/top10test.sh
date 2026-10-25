#!/bin/bash
# top10test.sh BOT NOTE -> submit BOT, replay the 20 top-10 groups (side a), wait, resubmit v25u, save matches to $S/test_<BOT>.json
S=/tmp/claude-0/-home-user-BattlecodeConversation/efdc7f3e-edfb-5016-b385-eb414f18c8fe/scratchpad;P=$S/proj;B=$1;NOTE=$2
rm -rf $P/bots/$B; cp -r /home/user/BattlecodeConversation/bots/$B $P/bots/$B; rm -rf $P/bots/$B/.cambc
python3 - "$P/bots/$B/src/main.cpp" "$B" "$NOTE" <<'PY'
import sys,time
p,b,n=sys.argv[1:4];s=open(p).read()
open(p,'w').write(f'// SUBMISSION NOTE ({b}, {time.strftime("%Y-%m-%d %H:%M UTC",time.gmtime())})\n// {n}\n// END NOTE\n'+s)
PY
cd $P && cambc submit bots/$B 2>&1 | tail -1
python3 - "$S" "$B" <<'PY'
import json,subprocess,time,sys
S,B=sys.argv[1:3]
spec=json.load(open(S+'/groups_spec.json'))
top=[s for s in spec if s[0][:8]!='4938a543' and s[2][0]=='a' and s[1][0] in('00corners','00expanse')]
G=[]
for opp,maps,sides,n in top:
    r=subprocess.run(['cambc','match-groups','create',opp,'--maps',','.join(maps),'--side','a','--json'],capture_output=True,text=True)
    try:G.append(json.loads(r.stdout).get('groupId'))
    except Exception:print('queue fail',r.stdout[-150:],r.stderr[-150:])
G=[g for g in G if g];print('queued',len(G),flush=True)
t0=time.time();done=[]
while time.time()-t0<3000:
    d=json.loads(subprocess.run(['cambc','matches','list','--team','me','--kind','unranked','--limit','100','--json'],capture_output=True,text=True).stdout or '{"matches":[]}')
    done=[m for m in d['matches'] if m['groupId'] in G and m['status']=='finished']
    if len(done)>=5*len(G):break
    time.sleep(45)
print('finished',len(done),flush=True)
json.dump(done,open(S+'/test_%s.json'%B,'w'))
PY
cd $P && cambc submit bots/v25u 2>&1 | tail -1
