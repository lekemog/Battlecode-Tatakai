"""Paired comparison of two logged runs on the same games: wins, camp/champion deaths. usage: pairdeaths.py DIR_A BOT_A DIR_B BOT_B"""
import json,glob,os,sys,collections
def load(D,bot):
    out={}
    for js in glob.glob(f'{D}/*.json'):
        tag=os.path.basename(js)[:-5]; key=tag.replace(bot,'BOT')
        ours='teamA' if '_'.join(tag.split('_')[1:]).startswith(bot+'_') else 'teamB'
        d=json.load(open(js)); c=collections.Counter()
        for e in d['events']:
            if e['kind']=='death' and e['owner'].get('team')==ours:
                for x in e['entries']: c['camp' if (x.get('target') or {}).get('kind')=='camp' else 'champ']+=1
        g={t['team']:int(t['submittedGems']) for t in d['teams']}
        out[key]=(d['match']['outcome']==ours, g[ours]-g['teamB' if ours=='teamA' else 'teamA'], c['camp'], c['champ'])
    return out
A=load(sys.argv[1],sys.argv[2]); B=load(sys.argv[3],sys.argv[4]); keys=sorted(set(A)&set(B))
t=collections.Counter()
for k in keys:
    a,b=A[k],B[k]
    for i,lab in ((0,'win'),(1,'margin'),(2,'camp'),(3,'champ')): t['a'+lab]+=a[i]; t['b'+lab]+=b[i]
    if a[0]!=b[0]: print(f"  {k}: {sys.argv[2]} {'W' if a[0] else 'L'} -> {sys.argv[4]} {'W' if b[0] else 'L'}")
n=len(keys)
print(f"{n} games: wins {t['awin']} -> {t['bwin']}, mean margin {t['amargin']/n:+.0f} -> {t['bmargin']/n:+.0f}, camp deaths/game {t['acamp']/n:.2f} -> {t['bcamp']/n:.2f}, champion deaths/game {t['achamp']/n:.2f} -> {t['bchamp']/n:.2f}")
