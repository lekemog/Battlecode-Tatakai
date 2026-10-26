"""deathstudy.py ZIP SIDE(0/1) -> each death of SIDE: round, enemies/allies within 5, champion types, gems carried, what killed (camp vs champ)."""
import json,sys,zipfile,tempfile,subprocess,os,collections
z,s=sys.argv[1],int(sys.argv[2]);t=tempfile.mkdtemp()
zipfile.ZipFile(z).extractall(t);rp=[os.path.join(a,f) for a,_,fs in os.walk(t) for f in fs if f.endswith('.repl26a')][0]
subprocess.run(['node','/home/claude/tools/replay/extract3.mjs','/home/claude/data/vis3/assets',rp,t+'/r.json'],capture_output=True)
R=json.load(open(t+'/r.json'))['rounds']
N=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','HoR']
P=lambda c:(c['position']['x'],c['position']['y']) if c.get('position') else None
cb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
summ=collections.Counter()
for r in range(2,len(R)):
  pv={c['entity']['index']:c for c in R[r-1]['champions']}
  for c in R[r]['champions']:
    p=pv.get(c['entity']['index'])
    if c['team']==s and p and p.get('alive') and not c.get('alive') and P(p):
      pp=P(p);en=[x for x in R[r-1]['champions'] if x['team']!=s and x.get('alive') and P(x) and cb(P(x),pp)<=5]
      al=[x for x in R[r-1]['champions'] if x['team']==s and x is not p and x.get('alive') and P(x) and cb(P(x),pp)<=5]
      key=f"{len(en)}v{len(al)+1}";summ[key]+=1
      if len(sys.argv)>3:print(r,N[p['type']],'hp',p['health'],'gems',p.get('gems'),'enemies',[N[x['type']] for x in en],'allies',len(al),'pos',pp)
print('deaths by (enemies near) v (us near):',sorted(summ.items(),key=lambda kv:-kv[1]))
