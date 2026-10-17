import json,subprocess,sys,os,time,re
def dl(mid,p):
    for t in range(8):
        r=subprocess.run(['cambc','matches','summary',mid,'--json','-o',p],capture_output=True,text=True)
        if r.returncode==0:return
        m=re.search(r'retry after (\d+)',r.stderr+r.stdout);time.sleep(int(m.group(1))+1 if m else 3)
ME='9c16b699-cad2-453e-8042-dae23ff934d8';D='/home/claude/data/ladder'
groups=json.load(open('/home/claude/data/ab/groups.json'))
tags=sys.argv[1:]
res={}
for g in groups:
    if g['tag'] not in tags:continue
    d=json.loads(subprocess.run(['cambc','match-groups','show',g['group'],'--json'],capture_output=True,text=True).stdout)
    for m in d['matches']:
        p=f"{D}/{m['matchId']}.json"
        if not os.path.exists(p):dl(m['matchId'],p)
        if not os.path.exists(p):continue
        j=json.load(open(p))
        us=[t for t in m['teams'] if t['teamId']==ME][0]['side'];us='team'+us.upper()
        gm={t['team']:int(t['submittedGems']) for t in j['teams']}
        th='teamB' if us=='teamA' else 'teamA'
        gold={'teamA':0,'teamB':0};de={'teamA':0,'teamB':0}
        for c in j['champions']:gold[c['team']]+=int(c['metrics']['earnedGold']);de[c['team']]+=int(c['metrics']['deaths'])
        key=(g['name'][:10],m['map'][:9])
        res.setdefault(key,{})[g['tag']]=(('W' if j['match']['outcome']==us else 'L'),gm[us]-gm[th],j['match']['roundsStarted'],de[us],gold[us]-gold[th])
tot={t:0 for t in tags}
for k,v in sorted(res.items()):
    print(f'{k[0]:10} {k[1]:9}',' | '.join(f"{t}:{v[t][0]}{v[t][1]:+5d} r{v[t][2]:4} d{v[t][3]:2}" if t in v else f'{t}:-' for t in tags))
    for t in tags:
        if t in v:tot[t]+=v[t][1]
print('sum gem margin',tot)
