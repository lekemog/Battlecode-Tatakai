"""Every bag (>=20 gems) carried by us vs them: banked or lost, size, hold time, heading to altar at loss.
usage: bags.py MAP"""
import json,os,sys,collections,statistics as st
MAP=sys.argv[1];sys.argv=['x'];exec(open('/home/claude/tools/replay/dataset.py').read().split('FEATS =')[0])
OUT='/home/claude/data/our_rep';idx=json.load(open(f'{OUT}/index.json'));M=load_map(MAP);alts=M.get('altars') or []
B={'US':[],'TH':[]};n=0
for mid,v in idx.items():
    if v['map']!=MAP or not str(v.get('cycle','')).startswith('c') or not os.path.exists(f'{OUT}/{mid}.json'):continue
    n+=1
    if n>40:break
    try:R=json.load(open(f'{OUT}/{mid}.json'))['rounds']
    except Exception:continue
    us=0 if v['side']=='a' else 1;cur={};trail=collections.defaultdict(list)
    def ad(p):return min(max(abs(p[0]-a[0]),abs(p[1]-a[1])) for a in alts) if alts else 0
    for t in range(10,len(R)):
        for c in R[t]['champions']:
            i=c['entity']['index'];S='US' if c['team']==us else 'TH';g=c.get('gems') or 0
            p=(c['position']['x'],c['position']['y']) if c.get('position') else None
            if p and c.get('alive'):trail[i].append(ad(p));trail[i]=trail[i][-8:]
            if i in cur:
                st0,peak=cur[i]
                if not c.get('alive'):
                    tr=trail[i];head=(tr[0]-tr[-1]) if len(tr)>=4 else 0
                    B[S].append(('lost',peak,t-st0,head,tr[-1] if tr else None));del cur[i]
                elif g<20:B[S].append(('banked',peak,t-st0,0,0));del cur[i]
                else:cur[i]=(st0,max(peak,g))
            elif g>=20 and c.get('alive'):cur[i]=(t,g)
print('==',MAP,'games',min(n,40))
for S in ('US','TH'):
    L=B[S];lost=[x for x in L if x[0]=='lost'];bk=[x for x in L if x[0]=='banked']
    if not L:continue
    print(f' {S}: bags {len(L)}, banked {len(bk)} ({len(bk)/len(L):.0%}), lost {len(lost)} | banked: median size {st.median(x[1] for x in bk) if bk else 0}, hold {st.median(x[2] for x in bk) if bk else 0}r | lost: median size {st.median(x[1] for x in lost) if lost else 0}, held {st.median(x[2] for x in lost) if lost else 0}r, closing on altar in last 8r {sum(1 for x in lost if x[3]>=2)}/{len(lost)}, median altar dist at death {st.median(x[4] for x in lost if x[4] is not None) if lost else 0}')
