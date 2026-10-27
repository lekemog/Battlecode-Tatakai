"""For camp deaths during a retreat: monster damage taken in the 10 rounds before the retreat began vs during it."""
import json,glob,os,sys,re,zipfile,collections,statistics
bot,D=sys.argv[1],sys.argv[2]; OUT={'retreat','camp-out','recall'}
pre=[];during=[];rounds=[];maxhp_frac=[]
def series(runs):
    v=[];
    for r in runs: v+= [float(r['value'])]*r['duration']
    return v
for js in glob.glob(f'{D}/*.json'):
    tag=os.path.basename(js)[:-5]; ours='a' if '_'.join(tag.split('_')[1:]).startswith(bot+'_') else 'b'; team='team'+ours.upper()
    st=json.load(open(js)); ids=sorted(c['id'] for c in st['roster']['champions'] if c['team']==team); slot={c:k for k,c in enumerate(ids)}
    md={x['owner']['id']:series(x['runs']) for x in st['championTimelines'] if x['metric']=='monsterDamageTaken' and x['owner'].get('team')==team}
    raw=zipfile.ZipFile(f'{D}/{tag}.repl26a').read(f'team-{ours}.stdout').decode('utf-8','replace')
    rows=collections.defaultdict(list); mx={}
    for m in re.finditer(r'T (\d+) (\d) ([a-z-]+) (-?\d+) (-?\d+)',raw):
        r,s,a,t,hp=m.groups(); rows[int(s)].append((int(r),a,int(hp))); mx[int(s)]=max(mx.get(int(s),0),int(hp))
    for v in rows.values(): v.sort()
    for e in st['events']:
        if e['kind']!='death' or e['owner'].get('team')!=team: continue
        cid=e['owner']['id']; s=slot.get(cid); ser=md.get(cid)
        for x in e['entries']:
            if (x.get('target') or {}).get('kind')!='camp' or not ser: continue
            rd=x['timestamp']['round']; L=[r for r in rows.get(s,[]) if r[0]<=rd]
            if not L or L[-1][1] not in OUT: continue
            i=len(L)-1
            while i>0 and L[i-1][1] in OUT: i-=1
            r0=L[i][0]
            if rd>=len(ser) or r0-10<0: continue
            a=ser[r0]-ser[max(0,r0-10)]; b=ser[min(rd,len(ser)-1)]-ser[r0]
            pre.append(a); during.append(b); rounds.append(rd-r0); maxhp_frac.append(b/max(1,mx.get(s,1)))
n=len(pre)
print(f'{n} camp deaths during a retreat')
print(f'monster damage in the 10 rounds BEFORE the retreat: median {statistics.median(pre):.0f}')
print(f'monster damage DURING the retreat (until death):   median {statistics.median(during):.0f}  ({100*statistics.median(maxhp_frac):.0f}% of max HP), over a median {statistics.median(rounds)} rounds')
print(f'share of deaths where the retreat itself took >25% of max HP from camps: {100*sum(f>.25 for f in maxhp_frac)/n:.0f}%')
