"""Paired gem margins from decoded replays: pairmargin.py TAG botA botB [botC...]
For every (opponent, map) played by all bots, compares our final gems minus theirs."""
import json,sys,os,statistics as st,collections
OUT='/home/claude/data/our_rep';TAG=sys.argv[1];B=sys.argv[2:]
idx=json.load(open(f'{OUT}/index.json'));res=json.load(open(f'{OUT}/{TAG}_results.json'))
M=collections.defaultdict(dict)
for k,(r,mid) in res.items():
    b,o,m=k.split('|')
    p=f'{OUT}/{mid}.json'
    if b not in B or mid not in idx or not os.path.exists(p):continue
    try:d=json.load(open(p))
    except Exception:continue
    us=0 if idx[mid]['side']=='a' else 1;g=d['rounds'][-1]['submittedGems']
    M[(o,m)][b]=g[us]-g[1-us]
common=[k for k,v in M.items() if all(b in v for b in B)]
print('games with all arms decoded:',len(common))
for b in B[1:]:
    diffs=[M[k][b]-M[k][B[0]] for k in common]
    if diffs:print(f'{b} minus {B[0]}: mean {st.mean(diffs):+.0f} gems, median {st.median(diffs):+.0f}, better in {sum(d>0 for d in diffs)}, worse in {sum(d<0 for d in diffs)}, same {sum(d==0 for d in diffs)}')
bymap=collections.defaultdict(list)
for k in common:bymap[k[1]].append(tuple(M[k][b] for b in B))
for m,v in sorted(bymap.items()):print(f'  {m:12}',' | '.join(f'{B[i]} {st.mean(x[i] for x in v):+.0f}' for i in range(len(B))))
