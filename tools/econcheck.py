"""Economy metrics for local runs made by localbehav.py (data/lb_<bot>_<map>): per game us/them team gold@300,
gems submitted @400, deaths. usage: econcheck.py MAP BOT [BOT...]"""
import json, sys, statistics as st
MAP = sys.argv[1]
for bot in sys.argv[2:]:
    out = f'/home/claude/data/lb_{bot}_{MAP}'
    try: idx = json.load(open(out + '/index.json'))
    except Exception: print(bot, MAP, 'missing'); continue
    rows = []
    for k, v in idx.items():
        try: R = json.load(open(f'{out}/{k}.json'))['rounds']
        except Exception: continue
        us = 0 if v['side'] == 'a' else 1
        def gold(t, tm): return sum(c.get('earnedGold', 0) for c in R[min(t, len(R) - 1)]['champions'] if c['team'] == tm)
        dead = [0, 0]; prev = {c['entity']['index']: c.get('alive') for c in R[10]['champions']}
        for t in range(11, len(R)):
            for c in R[t]['champions']:
                i = c['entity']['index']
                if prev.get(i) and not c.get('alive'): dead[0 if c['team'] == us else 1] += 1
                prev[i] = c.get('alive')
        rows.append((v['result'] == 'win', gold(300, us), gold(300, 1 - us), R[min(400, len(R) - 1)]['submittedGems'][us], R[min(400, len(R) - 1)]['submittedGems'][1 - us], dead[0], dead[1]))
    m = lambda i: st.mean(r[i] for r in rows)
    print(f'{bot:5} {MAP:9} n={len(rows)} wins {sum(r[0] for r in rows)} | gold@300 {m(1):.0f}/{m(2):.0f} | gems@400 {m(3):.0f}/{m(4):.0f} | deaths {m(5):.1f}/{m(6):.1f}', flush=True)
