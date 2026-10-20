"""quickgame.py A B MAPTAG -> run one local release game, decode, print per-100-round gems/gold/deaths per team and positions summary."""
import sys,subprocess,json,os,zipfile,tempfile,shutil,glob
A,B,M=sys.argv[1:4]
S=tempfile.mkdtemp(dir='/tmp/claude-0/-home-claude/1a6e1a21-0974-5904-af74-73034a4d3e04/scratchpad')
out=subprocess.run(['cambc','run',A,B,'--map',f'maps/{M}.map26a','--release','-o',S],cwd='/home/claude/proj',capture_output=True,text=True).stdout
print('\n'.join(l for l in out.split('\n') if l.strip().startswith(('A ','B '))))
z=glob.glob(f'{S}/*.repl26a')[0];zipfile.ZipFile(z).extractall(S)
subprocess.run(['node','/home/claude/tools/replay/extract.mjs','/home/claude/data/vis/assets',f'{S}/replay.repl26a',f'{S}/r.json'],capture_output=True)
R=json.load(open(f'{S}/r.json'))['rounds']
dead=[0,0];pa={};lost=[0,0];prev={}
marks={}
for t in range(5,len(R)):
    for c in R[t]['champions']:
        i=c['entity']['index'];w=c['team']
        if pa.get(i) and not c.get('alive'):dead[w]+=1;lost[w]+=prev.get(i,0)
        pa[i]=c.get('alive');prev[i]=c.get('gems') or 0
    if t%100==0:marks[t]=(list(R[t]['submittedGems']),[sum(c.get('earnedGold',0) for c in R[t]['champions'] if c['team']==w) for w in (0,1)],list(dead),list(lost))
for t,v in marks.items():print(t,'gems',v[0],'gold',v[1],'deaths',v[2],'bag-lost',v[3])
print('dir',S)
