import json,sys,os
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
NM={0:'ryth',1:'vesper',2:'vendetta',3:'cassi',4:'issac',5:'stellar',6:'prism',7:'marcella',8:'willow',9:'ren',10:'varg',11:'tavi',12:'heart'}
def run(mid,ourteam,maxr=250):
    d=json.load(open(f'dec/{mid}.json'));R=d['rounds']
    # spawn pos of each team: round-0 average
    sp={}
    R0=next(r for r in R if r['round']>=1 and sum(1 for c in r['champions'] if 'position' in c)>=len(r['champions'])>0)
    for t in (0,1):
        ps=[(c['position']['x'],c['position']['y']) for c in R0['champions'] if c['team']==t and 'position' in c]
        sp[t]=(sum(p[0] for p in ps)/len(ps),sum(p[1] for p in ps)/len(ps))
    out=[]
    prev=R[1]
    for r in R[2:]:
        if r['round']>maxr:break
        for c in r['champions']:
            if not c['alive']:
                pc=[x for x in prev['champions'] if x['entity']==c['entity']]
                if pc and pc[0]['alive'] and 'position' in pc[0]:
                    p=pc[0];pos=(p['position']['x'],p['position']['y'])
                    near_e=[(NM[x['type']],cheb(pos,(x['position']['x'],x['position']['y'])),x['health']) for x in prev['champions'] if x['team']!=c['team'] and x['alive'] and 'position' in x and cheb(pos,(x['position']['x'],x['position']['y']))<=7]
                    near_a=[(NM[x['type']],cheb(pos,(x['position']['x'],x['position']['y']))) for x in prev['champions'] if x['team']==c['team'] and x['alive'] and 'position' in x and x['entity']!=c['entity'] and cheb(pos,(x['position']['x'],x['position']['y']))<=7]
                    out.append(dict(r=r['round'],team=c['team'],who=NM[c['type']],pos=pos,hp=p['health'],maxhp=p['maxHealth'],gems=p['gems'],dist_own=round(cheb(pos,sp[c['team']])),dist_enemy=round(cheb(pos,sp[1-c['team']])),near_e=near_e,near_a=near_a))
        prev=r
    return out,sp
if __name__=='__main__':
    mid=sys.argv[1];ot=int(sys.argv[2])
    out,sp=run(mid,ot)
    print(mid,'spawns',sp)
    for o in out:
        print('US ' if o['team']==ot else 'OPP',o['r'],o['who'],o['pos'],f"hp {o['hp']:.0f}/{o['maxhp']:.0f} gems {o['gems']} dOwn {o['dist_own']} dEn {o['dist_enemy']} enemies7 {[(a,b) for a,b,_ in o['near_e']]} allies7 {o['near_a']}")
