import json,glob,sys,os,collections
bot=sys.argv[1];d=sys.argv[2]
L=collections.defaultdict(int);N=collections.defaultdict(int);M=collections.defaultdict(list)
for f in glob.glob(d+'/*/*.json'):
    b=os.path.basename(f)[:-5]
    if not b.startswith('bench') and '_' not in b: continue
    m,first,second=b.split('_',2)
    j=json.load(open(f))
    try:o=j['match']['outcome']
    except: continue
    a_is=(first==bot)
    won=(o=='teamA')==a_is
    N[m]+=1;L[m]+=(not won)
    g={t['team']:int(t['submittedGems']) for t in j['teams']}
    me='teamA' if a_is else 'teamB'
    M[m].append(g[me]-g['teamB' if a_is else 'teamA'])
for m in sorted(N,key=lambda m:-L[m]):
    print(f'{m:22s} losses {L[m]:2d}/{N[m]:2d} meanmargin {sum(M[m])/len(M[m]):+.0f}')
