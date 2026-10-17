"""Real-ladder A/B scrims. usage:
  ab.py create TAG OPP_ID MAP1,MAP2,...   (queue one 5-match group vs opponent, logged under TAG)
  ab.py status [TAG...]                    (results per tag: wins/finished, per opponent)
"""
import json,subprocess,sys,os,collections
ME='9c16b699-cad2-453e-8042-dae23ff934d8'
LOG='/home/claude/data/ab/groups.json'
def sh(a):
    r=subprocess.run(['cambc']+a,capture_output=True,text=True,cwd='/home/claude/proj')
    out=r.stdout.strip()
    if r.returncode!=0:raise SystemExit(r.stderr[-500:])
    return out
def load():return json.load(open(LOG)) if os.path.exists(LOG) else []
if sys.argv[1]=='create':
    tag,opp,maps=sys.argv[2:5]
    d=json.loads(sh(['match-groups','create',opp,'--maps',maps,'--json']))
    g=load();g.append({'tag':tag,'opp':opp,'name':d.get('teamName'),'group':d['groupId'],'maps':maps});json.dump(g,open(LOG,'w'),indent=1)
    print('queued',tag,d.get('teamName'),d['groupId'])
elif sys.argv[1]=='status':
    tags=sys.argv[2:]
    agg=collections.defaultdict(lambda:[0,0,0])
    for g in load():
        if tags and g['tag'] not in tags:continue
        d=json.loads(sh(['match-groups','show',g['group'],'--json']))
        res=[]
        for m in d['matches']:
            us=[t for t in m['teams'] if t['teamId']==ME][0]
            res.append((m['map'],us['result'] or m['status']))
        w=sum(r=='win' for _,r in res);f=sum(r in('win','loss','draw') for _,r in res)
        a=agg[g['tag']];a[0]+=w;a[1]+=f;a[2]+=len(res)
        print(f"{g['tag']:8} vs {g['name'][:20]:20} {w}/{f} done of {len(res)}  "+' '.join(f'{m[:6]}:{r[:4]}' for m,r in res))
    for t,(w,f,n) in agg.items():print(f'TOTAL {t}: {w}/{f} finished ({n} queued)')
