from pathlib import Path
import json,collections
root=Path(__file__).parent
names=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','HoR']
def dist(a,b):return max(abs(a['x']-b['x']),abs(a['y']-b['y']))
for mid,times in {'7a568552-0496-47aa-a018-67af3b520a35':[100,250,300,350,400,600], 'd148b5ea-d71d-4480-bff4-0fba938d6429':[730,750,768,779,800,809], '793352d2-2946-44a1-b89b-225a5879311d':[600,700,750,800,850,900]}.items():
 R={r['round']:r for r in json.loads((root/mid/'decoded.json').read_text())['rounds']};ev=json.loads((root/'fish-series-evidence.json').read_text());e=next(x for x in ev if x['id']==mid)
 print('\n',mid)
 for t in times:
  r=R[t];print('r',t,'banked',r['submittedGems'],'carry',[sum(c['gems']for c in r['champions']if c['team']==w and c['alive'])for w in (0,1)])
  if t in [300,750,800,809]:
   for c in r['champions']:
    print(c['entity']['index'],names[c['type']],c['team'],c.get('position'),c['alive'],'hp',round(c['health']),round(c['maxHealth']),'bag',c['gems'],'earned',c['earnedGold'],'str',round(c['strength']['effective']),'focus',round(c['focus']['effective']),'items',[(i,n)for i,n in enumerate(c['items'])if n],'channel',c['channelType'],c['channelTimer'])
 counts=collections.Counter()
 for death in e['deaths']:
  if death['team']!=1:continue
  t=max(0,death['r']-5);r=R[t];c=next(x for x in r['champions']if x['entity']['index']==death['id'])
  if not c.get('position')or not c['alive']:continue
  allies=[a for a in r['champions']if a['alive']and a['team']==1 and a['entity']['index']!=death['id']and dist(a['position'],c['position'])<=6]
  enemies=[a for a in r['champions']if a['alive']and a['team']==0 and dist(a['position'],c['position'])<=6]
  counts[(len(allies),len(enemies))]+=1
 print('fish death pre5 nearby (allies excluding self,enemies)',dict(counts));print('fish banks last', [b for b in e['banks']if b['team']==1][-12:])
