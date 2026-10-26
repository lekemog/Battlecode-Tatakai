"""Eight copycat validation: CC vs CAND on eight (both sides). Prints gems@400, gems lost on death, bank events, median bag, deaths, result."""
import subprocess,json,statistics as st,sys,shutil
cc=sys.argv[1]; cand=sys.argv[2] if len(sys.argv)>2 else 'v19n'; MAP=sys.argv[3] if len(sys.argv)>3 else 'eight'
subprocess.run(['python3','-I','/home/claude/tools/localbehav.py',cand,MAP,cc],capture_output=True,timeout=1500)
out=f'/home/claude/data/lb_{cand}_{MAP}';idx=json.load(open(out+'/index.json'));rows=[]
for k,v in idx.items():
    R=json.load(open(f'{out}/{k}.json'))['rounds'];op=1 if v['side']=='a' else 0
    lost=[0,0];banks=[[],[]];dead=[0,0];prev={};pa={}
    for t in range(20,len(R)):
        for c in R[t]['champions']:
            i=c['entity']['index'];w=0 if c['team']==op else 1;gm=c.get('gems') or 0
            if pa.get(i) and not c.get('alive'):dead[w]+=1;lost[w]+=prev.get(i,0)
            if i in prev and c.get('alive') and gm<prev[i]:banks[w].append(prev[i])
            pa[i]=c.get('alive');prev[i]=gm if c.get('alive') else 0
    s=R[min(400,len(R)-1)]['submittedGems']
    rows.append((v['result']!='win',s[op],s[1-op],lost[0],lost[1],len(banks[0]),len(banks[1]),st.median(banks[0]) if banks[0] else 0,st.median(banks[1]) if banks[1] else 0,dead[0],dead[1],R[-1]['submittedGems'][op],R[-1]['submittedGems'][1-op]))
shutil.rmtree(out,ignore_errors=True)
m=lambda i:st.mean(r[i] for r in rows)
print(f"{cc} vs {cand} [{MAP}]: cc wins {sum(r[0] for r in rows)}/{len(rows)} | gems@400 {m(1):.0f}/{m(2):.0f} | lost on death {m(3):.0f}/{m(4):.0f} | banks {m(5):.1f}/{m(6):.1f} | median bag {m(7):.0f}/{m(8):.0f} | deaths {m(9):.1f}/{m(10):.1f} | final {m(11):.0f}/{m(12):.0f}")
