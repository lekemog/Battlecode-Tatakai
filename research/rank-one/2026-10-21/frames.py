from pathlib import Path
import json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).parent
names=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','HoR']
plans={
'7a568552-0496-47aa-a018-67af3b520a35':[30,100,250,300,350,400,450,500,600,900,1200,1800],
'd148b5ea-d71d-4480-bff4-0fba938d6429':[30,100,300,600,700,730,750,768,779,790,800,809],
'793352d2-2946-44a1-b89b-225a5879311d':[30,100,300,600,700,750,800,850,900,1000,1200,1370]}
for mid,times in plans.items():
 d=json.loads((ROOT/mid/'decoded.json').read_text());R={r['round']:r for r in d['rounds']};fig,axes=plt.subplots(3,4,figsize=(20,16))
 for ax,t in zip(axes.flat,times):
  r=R[t];camps=[c for c in r['camps']if c.get('position')and c['health']>0]
  for c in camps:
   p=c['position'];ax.scatter(p['x'],p['y'],c=['#777777','#777777','#9b59b6','#d4ac0d','#111111','#111111'][c['type']],s=12,marker='x')
  for c in r['champions']:
   if not c['alive']or not c.get('position'):continue
   i=c['entity']['index'];p=c['position'];color='#2455a4'if c['team']==0 else '#cf302f'
   trail=[next((v.get('position') for v in R[k]['champions']if v['entity']['index']==i and v['alive']),None)for k in range(max(0,t-15),t+1)if k in R];trail=[p for p in trail if p]
   if trail:ax.plot([p['x']for p in trail],[p['y']for p in trail],c=color,alpha=.35,linewidth=1)
   ax.scatter(p['x'],p['y'],c=color,s=45,marker='o'if c['team']==0 else 's')
   ax.text(p['x']+.3,p['y']+.3,f'{i}:{names[c["type"]]}\n{c["health"]:.0f}/{c["maxHealth"]:.0f} g{c["gems"]}',fontsize=6,color=color)
  ax.set_title(f'r{t} | banked {r["submittedGems"]}',fontsize=11);ax.set_aspect('equal');ax.grid(alpha=.15);ax.invert_yaxis()
 fig.suptitle(f'{mid}\nBlue = procless; Red = Fish. Official decoded states, 15-round trails. Terrain not shown.',fontsize=15)
 fig.tight_layout(rect=[0,0,1,.95]);fig.savefig(ROOT/(mid+'-frames.png'),dpi=130);plt.close(fig)
 print(mid)
