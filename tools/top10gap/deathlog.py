# Inputs: /root/rep/ids.txt (match side opponent map, from results/panel/t10b_240.json) and /root/rep/<match>.zip from `cambc matches download`; decoded JSON in /root/rep/dec/ from tools/replay/extract5.mjs.
import zipfile,re,collections,sys
rows=[l.split() for l in open('/root/rep/ids.txt')]
pat=re.compile(r'death r(\d+) k(\d+) ((?:-?\d+:-?\d+:[a-z]+/[^:]*:e\d+d\d+a\d+:s-?\d+--?\d+ ?)+)')
tok=re.compile(r'(-?\d+):(-?\d+):([a-z]+)/([^:]*):e(\d+)d(\d+)a(\d+):s(-?\d+)-(-?\d+)')
D=[]
for mid,side,opp,m in rows:
    z=zipfile.ZipFile(f'/root/rep/{mid}.zip'); fn='team-a.stdout' if side=='a' else 'team-b.stdout'
    txt=z.read(fn).decode('latin1')
    for mm in pat.finditer(txt):
        turns=[tuple(t) for t in tok.findall(mm.group(3))]
        turns=[(int(a),int(b),c,d,int(e),int(f),int(g),int(h),int(i)) for a,b,c,d,e,f,g,h,i in turns]
        D.append(dict(opp=opp.split('-')[0],map=m,r=int(mm.group(1)),k=int(mm.group(2)),t=turns))
print('death lines',len(D))
C=collections.Counter()
for d in D:
    t=d['t']
    first=next((x for x in t if x[4]>0),None)   # first logged turn with an enemy in view
    if first is None: C['no enemy ever seen in last turns']+=1; continue
    i=t.index(first)
    pre=t[:i]
    # appeared close: first sighting at <=3 tiles
    C['first sight dist<=3' if first[5]<=3 else 'first sight dist 4-5' if first[5]<=5 else 'first sight dist>=6']+=1
    C['mode at first sight: '+first[2]+'/'+first[3]]+=1
    C['hp lost at first-sight turn >=30%' if (pre and pre[-1][1]>0 and (pre[-1][1]-first[1])/max(1,pre[-1][1])>=0.3) else 'no big hit at first sight']+=1
    C['allies within4 at first sight: %d'%min(first[6],2)]+=1
    C['allies within4 at last turn: %d'%min(t[-1][6],2)]+=1
    C['enemies at last turn: %d'%min(t[-1][4],4)]+=1
    C['sim at first sight our>their' if first[7]>first[8] else 'sim at first sight even/favourable' if first[7]>=0 else 'sim not run']+=1
    C['turns from first sight to death: %s'%('<=3' if -first[0]<=3 else '4-7' if -first[0]<=7 else '8+')]+=1
for k,v in sorted(C.items()): print(f'{v:4} {k}')
import pickle; pickle.dump(D,open('/tmp/claude-0/deaths.pkl','wb'))
