"""#45: ring-camp kills and every deposit on 02the_pack (single altar at (22,22) ringed by camp group 0).

usage: python3 -I tools/replay/ring45.py <decoded.json> <our_team_index: 0=teamA, 1=teamB>
The JSON comes from tools/replay/extract4.mjs (engine 2.0.0 replays).
Dead camps lose their position in snapshots, so camps are keyed by entity index from an early round.
Positions are end-of-round snapshots: a depositor may already have moved one or two tiles away."""
import json,sys
path=sys.argv[1]; us=int(sys.argv[2])
d=json.load(open(path)); R=d['rounds']
pos={c['entity']['index']:(c['position']['x'],c['position']['y']) for c in R[2]['camps']}
ring={c['entity']['index'] for c in R[2]['camps'] if c['group']==0}
cheb=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
A=(22,22)
dead={}
for r in R:
    for c in r['camps']:
        e=c['entity']['index']
        if e in ring and c['health']<=0 and e not in dead:
            near=[(ch['team'],ch['type'],cheb((ch['position']['x'],ch['position']['y']),pos[e])) for ch in r['champions'] if ch['alive'] and 'position' in ch]
            near=[n for n in near if n[2]<=4]
            dead[e]=(r['round'],pos[e],cheb(pos[e],A),near)
print('ring camps killed:',len(dead))
for e,(rd,p,da,near) in sorted(dead.items(),key=lambda t:t[1][0]):
    print(f'  r{rd} camp {p} ring-dist {da} near(team,type,dist)={near}')
# deposits
prev=[0,0]
for r in R:
    sg=r['submittedGems']
    for t in (0,1):
        if sg[t]!=prev[t]:
            who='US' if t==us else 'THEM'
            chs=[(ch['type'],(ch['position']['x'],ch['position']['y']),cheb((ch['position']['x'],ch['position']['y']),A)) for ch in r['champions'] if ch['team']==t and 'position' in ch and ch['alive']]
            close=[c for c in chs if c[2]<=6]
            print(f'deposit r{r["round"]} {who} +{sg[t]-prev[t]} -> {sg[t]}  champs<=6 of altar: {close}')
    prev=list(sg)
