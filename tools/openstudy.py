"""openstudy.py ZIP SIDE -> opening comparison (first 200 rounds): per champion gold, items, first camp kills, recalls/shops."""
import json,sys,zipfile,tempfile,subprocess,os,collections
z,s=sys.argv[1],int(sys.argv[2]);t=tempfile.mkdtemp()
zipfile.ZipFile(z).extractall(t);rp=[os.path.join(a,f) for a,_,fs in os.walk(t) for f in fs if f.endswith('.repl26a')][0]
subprocess.run(['node','/home/claude/tools/replay/extract3.mjs','/home/claude/data/vis3/assets',rp,t+'/r.json'],capture_output=True)
R=json.load(open(t+'/r.json'))['rounds']
N=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','HoR']
G=['Mon','Pow','Dur','Tre','Jun','Hom','Bru'];K=['Ss','Se','Fs','Fe','Hs','He']
P=lambda c:(c['position']['x'],c['position']['y'])
cb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
tn=['wolf','elk','gem','gold','mono','golem']
for team,lab in ((s,'US'),(1-s,'TOP')):
  print('==',lab)
  for r in (50,100,150,200):
    row=[]
    for c in R[r]['champions']:
      if c['team']!=team:continue
      it=[G[k//6]+K[k%6] for k,x in enumerate(c.get('items') or []) if x for _ in range(x if isinstance(x,int) else 1)]
      row.append(f"{N[c['type']][:5]} g{c.get('earnedGold',0)} hp{c.get('maxHealth')} {'/'.join(it)}")
    print(f' r{r}:',' | '.join(row))
  seq=[]
  for r in range(1,200):
    pv={c['entity']['index']:c for c in R[r-1]['camps']}
    for c in R[r]['camps']:
      p=pv.get(c['entity']['index'])
      if p and p['health']>0 and c['health']<=0 and p.get('position'):
        al=[h for h in R[r]['champions'] if h.get('alive') and h.get('position')]
        b=min(al,key=lambda h:cb(P(h),P(p))) if al else None
        if b and b['team']==team: seq.append(f"r{r}{tn[p['type']]}")
  print(' kills<200:',len(seq),' '.join(seq[:25]))
