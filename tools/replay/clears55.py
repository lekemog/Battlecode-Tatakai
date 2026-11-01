"""#55: camp-group captures per team over time from a decoded replay (extract4.mjs output).
usage: python3 -I tools/replay/clears55.py <decoded.json> <our_team_index> [bin=100]
A capture = a group going from state 2 (cleared, reward available) to 3 (claimed); the team is the captureTeam of the round before.
Prints captures per bin for us/them, the group table (camps, hp) and, for each group, first capture round and team."""
import json,sys
from collections import Counter,defaultdict
path=sys.argv[1]; us=int(sys.argv[2]); BIN=int(sys.argv[3]) if len(sys.argv)>3 else 100
d=json.load(open(path)); R=d['rounds']
camps=R[2]['camps']; size=Counter(c['group'] for c in camps)
hp={}; 
for c in camps: hp[c['group']]=hp.get(c['group'],0)+c['maxHealth']
pos=defaultdict(list)
for c in camps: pos[c['group']].append((c['position']['x'],c['position']['y']))
cen={g:(sum(p[0] for p in v)//len(v),sum(p[1] for p in v)//len(v)) for g,v in pos.items()}
prev=None; cap=[]  # (round, group, team)
val={}  # group -> (gems, gold) seen on the first claim: growth of that team's carried gems / earned gold across the claim round
prevcar=None
for r in R:
    st=[(g['state'],g['captureTeam']) for g in r['groups']]
    if prev:
        for i,(s,t) in enumerate(st):
            if s==3 and prev[i][0]==2 and prev[i][1] in (0,1): cap.append((r['round'],i,prev[i][1]))
    car=[sum(c['gems'] for c in r['champions'] if c['team']==t and c['alive']) for t in (0,1)]
    gold=[sum(c['earnedGold'] for c in r['champions'] if c['team']==t) for t in (0,1)]
    if prev and prevcar:
        for i,(s_,t_) in enumerate(st):
            if s_==3 and prev[i][0]==2 and prev[i][1] in (0,1) and i not in val:
                t=prev[i][1]; val[i]=(car[t]-prevcar[0][t], gold[t]-prevcar[1][t])
    prevcar=(car,gold)
    prev=st
O,T=us,1-us
bins=defaultdict(lambda:[0,0,0,0])
for rd,g,t in cap:
    b=bins[rd//BIN*BIN]; b[0 if t==O else 1]+=1; b[2 if t==O else 3]+=size[g]
print('bin  | captures us/them | camps captured us/them')
for b in sorted(bins): print(f'{b:5d} | {bins[b][0]:3d}/{bins[b][1]:3d} | {bins[b][2]:3d}/{bins[b][3]:3d}')
print('totals captures us/them', sum(1 for c in cap if c[2]==O), sum(1 for c in cap if c[2]==T), ' groups', len(size), 'camps', sum(size.values()), 'respawn', sorted({(g.get('respawnRounds')) for g in R[2]['groups']}))
first={}
for rd,g,t in cap:
    first.setdefault(g,(rd,'us' if t==O else 'them'))
rows=sorted(size,key=lambda g:-size[g]*0+hp[g])
print('group: camps hp centre first-capture')
for g in sorted(size,key=lambda g:(size[g],hp[g])):
    n=sum(1 for c in cap if c[1]==g)
    print(f' g{g}: n{size[g]} hp{hp[g]} at{cen[g]} first={first.get(g)} captures={n} (us {sum(1 for c in cap if c[1]==g and c[2]==O)}) reward(gems,gold)~{val.get(g)}')
