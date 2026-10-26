#!/bin/bash
# midtest.sh BOT LABEL [NOTE] -> (submit BOT unless v25u), queue 20 groups vs the 10 mid teams (2 map sets, side a), wait, save, restore v25u
S=/tmp/claude-0/-home-user-BattlecodeConversation/efdc7f3e-edfb-5016-b385-eb414f18c8fe/scratchpad;P=$S/proj;B=$1;L=$2;NOTE=$3
if [ "$B" != "v25u" ]; then
 rm -rf $P/bots/$B; cp -r /home/user/BattlecodeConversation/bots/$B $P/bots/$B; rm -rf $P/bots/$B/.cambc
 python3 - "$P/bots/$B/src/main.cpp" "$B" "$NOTE" <<'PY'
import sys,time
p,b,n=sys.argv[1:4];s=open(p).read()
open(p,'w').write(f'// SUBMISSION NOTE ({b}, {time.strftime("%Y-%m-%d %H:%M UTC",time.gmtime())})\n// {n}\n// END NOTE\n'+s)
PY
 cd $P && cambc submit bots/$B 2>&1 | tail -1
fi
python3 - "$S" "$L" <<'PY'
import json,subprocess,time,sys
S,L=sys.argv[1:3]
teams=json.load(open(S+'/mid_teams.json'))
sets=[['00corners','00contest','00eight','00monolith','01gold_rush'],['00expanse','00lanes','00lost_world','00rows','00rushbait_v2']]
G=[]
for t in teams:
    for ms in sets:
        for attempt in range(40):
            r=subprocess.run(['cambc','match-groups','create',t,'--maps',','.join(ms),'--side','a','--json'],capture_output=True,text=True)
            try:
                g=json.loads(r.stdout).get('groupId')
                if g:G.append(g);break
            except Exception:pass
            time.sleep(60)   # quota wait
print('queued',len(G),flush=True)
t0=time.time();done=[]
while time.time()-t0<3600:
    d=json.loads(subprocess.run(['cambc','matches','list','--team','me','--kind','unranked','--limit','100','--json'],capture_output=True,text=True).stdout or '{"matches":[]}')
    done=[m for m in d['matches'] if m['groupId'] in G and m['status']=='finished']
    if len(done)>=5*len(G):break
    time.sleep(45)
print('finished',len(done),flush=True)
json.dump(done,open(S+'/mid_%s.json'%L,'w'))
PY
if [ "$B" != "v25u" ]; then cd $P && cambc submit bots/v25u 2>&1 | tail -1; fi
