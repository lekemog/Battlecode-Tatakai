import json,glob,os,sys,statistics as st
C,B,D=sys.argv[1:4]
R={C:[],B:[]};G={C:[],B:[]}
for f in glob.glob(D+'/*.json'):
    t=os.path.basename(f)[:-5]
    if t=='manifest':continue
    j=json.load(open(f));rest=t.split('_',1)[1];first=rest.split('_')[0]
    sides={first:'teamA',(B if first==C else C):'teamB'}
    for bot,tm in sides.items():
        ids={c['id'] for c in j['roster']['champions'] if c['team']==tm}
        s=sorted((x['timestamp']['round'],int(x['value'])) for e in j['events'] if e['kind']=='gemSubmission' and e['owner'].get('id') in ids for x in e['entries'])
        if s:R[bot].append(s[0][0])
        G[bot].append(sum(v for r,v in s if r<=200))
for b in(C,B):print(b,'first deposit median',st.median(R[b]),'mean',round(st.mean(R[b])),'banked<=r200 mean',round(st.mean(G[b]),1))
