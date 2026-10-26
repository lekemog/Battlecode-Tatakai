"""elitestudy.py MAP -> download high-elo matches (Mohnish v5 vs 1820-1907 teams) on MAP, decode, report how the elite side plays."""
import csv,json,os,subprocess,sys,zipfile,tempfile,shutil,collections,statistics as st
MAP=sys.argv[1]
R=[r for r in csv.DictReader(open('/home/claude/data/ext/MohnishDhangar_Cambc/match-data/v5/prepared-high-elo/matches.csv')) if r['map_name']==MAP]
seen=set();out=[]
for r in R:
    if r['replay_sha256'] in seen:continue
    seen.add(r['replay_sha256'])
    D='/home/claude/data/elite';z=f'{D}/{r["match_id"]}.zip'
    if not os.path.exists(z):subprocess.run(['cambc','matches','download',r['match_id'],'-o',z],capture_output=True)
    tmp=tempfile.mkdtemp(dir=D)
    try:
        zipfile.ZipFile(z).extractall(tmp)
        subprocess.run(['node','/home/claude/tools/replay/extract3.mjs','/home/claude/data/vis3/assets',f'{tmp}/replay.repl26a',f'{tmp}/r.json'],capture_output=True)
        Rd=json.load(open(f'{tmp}/r.json'))['rounds']
    except Exception as e:
        shutil.rmtree(tmp,ignore_errors=True);continue
    shutil.rmtree(tmp,ignore_errors=True)
    elite=1 if r['our_side']=='A' else 0   # Mohnish is our_side; elite is the other team (0=A,1=B)
    T=len(Rd)-1
    def gold(t,w):return sum(c.get('earnedGold',0) for c in Rd[min(t,T)]['champions'] if c['team']==w)
    dead=[0,0];pa={};kills=collections.Counter();first_gem=[None,None]
    for t in range(5,len(Rd)):
        for c in Rd[t]['champions']:
            i=c['entity']['index']
            if pa.get(i) and not c.get('alive'):dead[c['team']]+=1
            pa[i]=c.get('alive')
        for w in (0,1):
            if first_gem[w] is None and Rd[t]['submittedGems'][w]>0:first_gem[w]=t
        pc={c['entity']['index']:c for c in Rd[t-1]['camps']}
        for c in Rd[t]['camps']:
            p=pc.get(c['entity']['index'])
            if p and p['health']>0 and c['health']<=0 and p.get('position'):
                al=[h for h in Rd[t]['champions'] if h.get('alive') and h.get('position')]
                if al:
                    b=min(al,key=lambda h:max(abs(p['position']['x']-h['position']['x']),abs(p['position']['y']-h['position']['y'])))
                    kills[(b['team'],p['type'])]+=1
    names=[[c.get('type') for c in Rd[30]['champions'] if c['team']==w] for w in (0,1)]
    out.append(dict(opp=r['opponent'],elo=r['opponent_elo'],rounds=T,gems=[Rd[T]['submittedGems'][elite],Rd[T]['submittedGems'][1-elite]],
        gold150=[gold(150,elite),gold(150,1-elite)],gold600=[gold(600,elite),gold(600,1-elite)],goldend=[gold(T,elite),gold(T,1-elite)],
        deaths=[dead[elite],dead[1-elite]],first_gem=[first_gem[elite],first_gem[1-elite]],
        kills_elite={str(k[1]):v for k,v in kills.items() if k[0]==elite},kills_other={str(k[1]):v for k,v in kills.items() if k[0]!=elite},draft_elite=names[elite]))
json.dump(out,open(f'/home/claude/data/elite_{MAP}.json','w'),indent=1)
print(MAP,'unique games',len(out))
m=lambda f:st.mean(f(x) for x in out) if out else 0
print(' elite vs Mohnish: gems %.0f/%.0f  gold@150 %.0f/%.0f  gold@600 %.0f/%.0f  gold end %.0f/%.0f  deaths %.1f/%.1f  rounds %.0f'%(m(lambda x:x['gems'][0]),m(lambda x:x['gems'][1]),m(lambda x:x['gold150'][0]),m(lambda x:x['gold150'][1]),m(lambda x:x['gold600'][0]),m(lambda x:x['gold600'][1]),m(lambda x:x['goldend'][0]),m(lambda x:x['goldend'][1]),m(lambda x:x['deaths'][0]),m(lambda x:x['deaths'][1]),m(lambda x:x['rounds'])))
ke=collections.Counter();ko=collections.Counter()
for x in out:ke.update(x['kills_elite']);ko.update(x['kills_other'])
print(' camp kills per game by type (0 wolf,1 elk,2 gem cl,3 gold cl,4 monolith): elite',{k:round(v/len(out),1) for k,v in sorted(ke.items())},'other',{k:round(v/len(out),1) for k,v in sorted(ko.items())})
print(' elite drafts',collections.Counter(tuple(sorted(x['draft_elite'])) for x in out).most_common(4))
print(' first gem banked round (elite/other) median',st.median([x['first_gem'][0] or 9999 for x in out]),st.median([x['first_gem'][1] or 9999 for x in out]))
