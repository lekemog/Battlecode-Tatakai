"""Outcomes per 25-round window split by our posture (defensive = logged agg>=40). usage: posture.py MAP..."""
import json,os,re,sys,collections,statistics as st
OUT='/home/claude/data/our_rep';idx=json.load(open(f'{OUT}/index.json'))
for MAP in sys.argv[1:]:
    S={True:collections.Counter(),False:collections.Counter()}
    for mid,v in idx.items():
        if v['map']!=MAP or not str(v.get('cycle','')).startswith('c') or not os.path.isdir(f'{OUT}/{mid}') or not os.path.exists(f'{OUT}/{mid}.json'):continue
        txt=''.join(open(f'{OUT}/{mid}/{f}','rb').read().replace(b'\x00',b'').decode('utf8','ignore') for f in os.listdir(f'{OUT}/{mid}') if f.endswith('.stdout'))
        win={}
        for r,a in re.findall(r'P3 r=(\d+) .* agg=(\d+)',txt):win[int(r)//25]=max(win.get(int(r)//25,0),int(a))
        if not win:continue
        try:R=json.load(open(f'{OUT}/{mid}.json'))['rounds']
        except Exception:continue
        us=0 if v['side']=='a' else 1;pa={};pg={}
        for t in range(10,len(R)):
            w=t//25
            if w not in win:continue
            dfn=win[w]>=40;C=S[dfn];C['rounds']+=1
            for c in R[t]['champions']:
                i=c['entity']['index'];g=c.get('gems') or 0;me=c['team']==us
                if pa.get(i) and not c.get('alive'):C['our_deaths' if me else 'their_deaths']+=1
                if c.get('alive') and i in pg and g<pg[i]:C['our_banked' if me else 'their_banked']+=pg[i]
                pa[i]=c.get('alive');pg[i]=g
    print('==',MAP)
    for k in (False,True):
        C=S[k];n=max(1,C['rounds'])/100
        print('  ','DEFENSIVE' if k else 'normal   ',f"share {C['rounds']/max(1,S[True]['rounds']+S[False]['rounds']):.2f} | per 100 rounds: our deaths {C['our_deaths']/n:.1f}, their deaths {C['their_deaths']/n:.1f}, we bank {C['our_banked']/n:.0f}, they bank {C['their_banked']/n:.0f}")
