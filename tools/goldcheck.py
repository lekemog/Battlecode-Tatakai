"""Gold @300/@600 and central-zone time for local contest runs (reads data/lb_<bot>_contest)."""
import json,sys,statistics as st,glob,os
C105=[(22,31),(27,18),(18,27),(31,22)]
def d(a,b):return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
for bot in sys.argv[1:]:
    out=f'/home/claude/data/lb_{bot}_contest';idx=json.load(open(out+'/index.json'));g3=[[],[]];g6=[[],[]];cz=[0,0];tz=[0,0];w=0
    for k,v in idx.items():
        R=json.load(open(f'{out}/{k}.json'))['rounds'];us=0 if v['side']=='a' else 1;w+=v['result']=='win'
        for T,acc in ((300,g3),(600,g6)):
            for i,tm in enumerate((us,1-us)):acc[i].append(sum(c.get('earnedGold',0) for c in R[min(T,len(R)-1)]['champions'] if c['team']==tm))
        for t in range(30,min(600,len(R)),3):
            for c in R[t]['champions']:
                if c['team']==us and c.get('alive') and c.get('position'):
                    tz[0]+=1;cz[0]+=any(d((c['position']['x'],c['position']['y']),q)<=3 for q in C105)
    print(bot,'games',len(idx),'wins',w,f'| team gold @300 {st.mean(g3[0]):.0f}/{st.mean(g3[1]):.0f} @600 {st.mean(g6[0]):.0f}/{st.mean(g6[1]):.0f} | our central-105 time {100*cz[0]/tz[0]:.0f}%')
