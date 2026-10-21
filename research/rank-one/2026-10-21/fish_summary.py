from pathlib import Path
import json,collections,statistics,hashlib
root=Path(__file__).parent
out=[]
for f in sorted(root.glob('*/decoded.json')):
 d=json.loads(f.read_text());rs=list({r['round']:r for r in d['rounds'] if r['round']>=0}.values());prev={};deaths=[];banks=[];score=[]
 for r in rs:
  for c in r['champions']:
   i=c['entity']['index'];p=prev.get(i)
   if p and p['alive'] and not c['alive']:deaths.append({'r':r['round'],'id':i,'team':c['team'],'type':c['type'],'pos':p.get('position'),'gems':p['gems']})
   if p and p['alive'] and c['alive'] and c['gems']<p['gems']:banks.append({'r':r['round'],'id':i,'team':c['team'],'gems':p['gems']-c['gems'],'pos':c['position']})
   prev[i]=c
  if not score or r['submittedGems']!=score[-1][1]:score.append([r['round'],r['submittedGems']])
 s={'id':f.parent.name,'engine':d['version'],'final_round':rs[-1]['round'],'gems':rs[-1]['submittedGems'],'outcome':rs[-1]['outcome'],'draft':[(c['entity']['index'],c['team'],c['type'])for c in rs[25]['champions']],'deaths':deaths,'banks':banks,'score_changes':score,'snapshots':[],'sha256':hashlib.sha256((f.parent/'replay.repl26a').read_bytes()).hexdigest()}
 for t in [30,50,100,150,300,600,900,1200,1500,1800,rs[-1]['round']]:
  if t>rs[-1]['round']:continue
  r=min(rs,key=lambda r:abs(r['round']-t))
  s['snapshots'].append({'r':r['round'],'gems':r['submittedGems'],'gold':[sum(c['earnedGold']for c in r['champions']if c['team']==w)for w in(0,1)],'deaths':[sum(v['team']==w and v['r']<=t for v in deaths)for w in(0,1)],'alive':[sum(c['alive']and c['team']==w for c in r['champions'])for w in(0,1)],'items':[(c['entity']['index'],c['items'])for c in r['champions']],'hp':[(c['entity']['index'],round(c['health']),round(c['maxHealth']))for c in r['champions']]})
 out.append(s)
 print('\n',s['id'],s['engine'],'r',s['final_round'],'gems',s['gems'],'deaths',collections.Counter(v['team']for v in deaths),'draft',s['draft']);print('first banks',banks[:10]);print('score',score[::max(1,len(score)//12)]);print('timeline',[(x['r'],x['gold'],x['gems'],x['deaths'])for x in s['snapshots']])
(root/'fish-series-evidence.json').write_text(json.dumps(out,indent=2))
