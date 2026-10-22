"""Summarise tools/t3engine103.ps1 output: results plus spawnblock.py mechanism numbers per decoded game.
usage: python tools/t3engine103_report.py OUTDIR      (files named MAP__BOT__OPP__SIDE.json; BOT plays SIDE)"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spawnblock import analyse

out = sys.argv[1]
for p in sorted(glob.glob(os.path.join(out, '*.json'))):
    name = os.path.basename(p)[:-5]
    parts = name.split('__')
    if len(parts) != 4: continue
    mp, bot, opp, side = parts; side = int(side)
    d = json.load(open(p, encoding='utf-8'))
    R = [x for x in d['rounds'] if x['phase'] != 12]; L = R[-1]
    g = L['submittedGems']; gold = [sum(c['earnedGold'] for c in L['champions'] if c['team'] == t) for t in (0, 1)]
    win = g[side] > g[1 - side] or (g[side] == g[1 - side] and gold[side] > gold[1 - side])
    m = analyse(p, side)
    print(f"{mp:7} {bot:20} vs {opp:20} side {side} {'WIN ' if win else 'loss'} {g[side]:>4}-{g[1 - side]:<4} | due_blocked {m['due_blocked']:>4}"
          f" worst {m['worst_block'][0]:>4}r g{m['worst_block'][1]} | respawns {m['respawns']:>3} max delay {m['max_delay']:>4} total {m['total_delay']:>5}"
          f" | stuck>=10r {len(m['stuck_10'])}" + (f" {m['stuck_10'][:2]}" if m['stuck_10'] else ''))
