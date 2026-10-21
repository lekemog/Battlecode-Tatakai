"""deathctx.py ZIP SIDE -> for each 1-enemy death of SIDE: HP 10 rounds before, distance to killer over last 8 rounds (approach/flee), enemy HP."""
import json,sys,zipfile,tempfile,subprocess,os
z,s=sys.argv[1],int(sys.argv[2]);t=tempfile.mkdtemp()
zipfile.ZipFile(z).extractall(t);rp=[os.path.join(a,f) for a,_,fs in os.walk(t) for f in fs if f.endswith('.repl26a')][0]
subprocess.run(['node','/home/claude/tools/replay/extract3.mjs','/home/claude/data/vis3/assets',rp,t+'/r.json'],capture_output=True)
R=json.load(open(t+'/r.json'))['rounds']
N=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','HoR']
P=lambda c:(c['position']['x'],c['position']['y']) if c.get('position') else None
cb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
def find(r,i):
  for c in R[r]['champions']:
    if c['entity']['index']==i:return c
for r in range(10,len(R)):
  pv={c['entity']['index']:c for c in R[r-1]['champions']}
  for c in R[r]['champions']:
    p=pv.get(c['entity']['index'])
    if c['team']==s and p and p.get('alive') and not c.get('alive') and P(p):
      en=[x for x in R[r-1]['champions'] if x['team']!=s and x.get('alive') and P(x) and cb(P(x),P(p))<=5]
      if len(en)!=1:continue
      e=en[0];i=c['entity']['index'];j=e['entity']['index']
      hist=[]
      for k in range(r-10,r):
        a,b=find(k,i),find(k,j)
        if a and b and P(a) and P(b) and a.get('alive'):hist.append((int(a['health']),cb(P(a),P(b)) if b.get('alive') else None,int(b['health']) if b.get('alive') else None))
      print(r,N[p['type']],'vs',N[e['type']],f"maxhp {p['maxHealth']} vs {e['maxHealth']}",'hist(hp,dist,enemyhp):',hist[::2])
