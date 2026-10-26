"""rankwatch.py SINCE STEP -> poll ranked every 5 min; exit (printing record) once STEP more finished games exist since SINCE than at start."""
import json,subprocess,sys,time,collections
SINCE=sys.argv[1];STEP=int(sys.argv[2]);T='9c16b699-cad2-453e-8042-dae23ff934d8'
def rec():
    d=json.loads(subprocess.run(['cambc','matches','list','--team',T,'--kind','ranked','--limit','100','--json'],capture_output=True,text=True,timeout=120).stdout)
    return [(x['createdAt'],x['map'],[t for t in x['teams'] if t.get('teamId')==T][0].get('result')) for x in d['matches'] if x['status']=='finished' and x['createdAt']>=SINCE]
r0=len(rec())
while True:
    time.sleep(300)
    try: r=rec()
    except Exception: continue
    if len(r)>=max(r0,0)+STEP or len(r)>=r0+STEP: break
w=sum(a=='win' for *_,a in r)
m=collections.defaultdict(lambda:[0,0])
for _,mp,a in r: m[mp][0]+=a=='win';m[mp][1]+=1
try: rank=json.loads(subprocess.run(['cambc','match-groups','quota','--json'],capture_output=True,text=True,timeout=120).stdout).get('requesterRank')
except Exception: rank='?'
print(f'{w}/{len(r)} since {SINCE} rank {rank}')
print(', '.join(f'{k} {a}/{n}' for k,(a,n) in sorted(m.items(),key=lambda kv:kv[1][0]-kv[1][1])))
last=[a[0] for *_,a in sorted(r)[-10:]];print('last10',''.join(last))
