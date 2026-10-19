"""Validate a contest copycat vs v19n locally: run both sides, report copycat central time, gold@600 both, deaths, result."""
import subprocess,json,statistics as st,sys,shutil
cc=sys.argv[1]; cand=sys.argv[2] if len(sys.argv)>2 else 'v19n'
subprocess.run(['python3','-I','/home/claude/tools/localbehav.py',cand,'contest',cc],capture_output=True,timeout=1500)
C105=[(22,31),(27,18),(18,27),(31,22)]
def d(a,b):return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
out=f'/home/claude/data/lb_{cand}_contest';idx=json.load(open(out+'/index.json'));cz=tz=0;rows=[]
for k,v in idx.items():
    R=json.load(open(f'{out}/{k}.json'))['rounds'];op=1 if v['side']=='a' else 0
    g=lambda tm:sum(c.get('earnedGold',0) for c in R[min(600,len(R)-1)]['champions'] if c['team']==tm)
    dead=[0,0];prev={c['entity']['index']:c.get('alive') for c in R[10]['champions']}
    for t in range(11,len(R)):
        for c in R[t]['champions']:
            i=c['entity']['index']
            if prev.get(i) and not c.get('alive'):dead[0 if c['team']==op else 1]+=1
            prev[i]=c.get('alive')
    for t in range(30,min(600,len(R)),3):
        for c in R[t]['champions']:
            if c['team']==op and c.get('alive') and c.get('position'):tz+=1;cz+=any(d((c['position']['x'],c['position']['y']),q)<=3 for q in C105)
    rows.append((v['result']!='win',g(op),g(1-op),dead[0],dead[1],R[-1]['submittedGems'][op],R[-1]['submittedGems'][1-op]))
shutil.rmtree(out,ignore_errors=True)
m=lambda i:st.mean(r[i] for r in rows)
print(f"{cc} vs {cand}: cc wins {sum(r[0] for r in rows)}/{len(rows)} | central {100*cz/max(1,tz):.0f}% | gold@600 cc {m(1):.0f} {cand} {m(2):.0f} (x{m(1)/max(1,m(2)):.2f}) | deaths cc {m(3):.1f} {cand} {m(4):.1f} | final gems cc {m(5):.0f} {cand} {m(6):.0f}")
