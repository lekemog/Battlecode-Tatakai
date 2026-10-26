"""stuck.py R.JSON TEAM [STDOUT] -> windows where a living champion of TEAM moved <=2 tiles and earned no gold for >=40 rounds."""
import json,sys
R=json.load(open(sys.argv[1]))['rounds'];T=int(sys.argv[2])
logs={}
if len(sys.argv)>3:
    for l in open(sys.argv[3],errors='ignore').read().replace('\x00','').split('\n'):
        p=l.split()
        if len(p)>4 and p[0]=='T':logs.setdefault(int(p[2]),[]).append((int(p[1]),p[3],p[4]))
ids=[c['entity']['index'] for c in R[1]['champions'] if c['team']==T]
for i in ids:
    start=None
    for t in range(20,len(R)):
        c=[x for x in R[t]['champions'] if x['entity']['index']==i][0]
        p=c.get('position');g=c.get('earnedGold',0)
        if not c.get('alive') or not p:start=None;continue
        if start is None:start=(t,p['x'],p['y'],g);continue
        if max(abs(p['x']-start[1]),abs(p['y']-start[2]))>2 or g!=start[3]:
            if t-start[0]>=40:print('champ',i,'type',c.get('type'),'rounds',start[0],'-',t,'at',(start[1],start[2]))
            start=(t,p['x'],p['y'],g)
    if start and len(R)-start[0]>=40:print('champ',i,'rounds',start[0],'- end at',(start[1],start[2]))
