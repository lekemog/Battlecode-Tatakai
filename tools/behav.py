"""Behaviour report from scrim replays: decode new scrim games and compare per-map behaviour by bot version.
usage: behav.py MAP[,MAP] [BOT,BOT]   (default bots: every bot with games on those maps)
Metrics are per-game means for us vs them: camp pickups by size, gems @200/@400, deaths, max HP @300,
first tribute round, bank events; plus our death causes from the audit classifier."""
import json, os, sys, zipfile, subprocess, collections, re
D = '/home/claude/data'; OUT = f'{D}/scrim_rep'; os.makedirs(OUT, exist_ok=True)
maps = sys.argv[1].split(','); want = sys.argv[2].split(',') if len(sys.argv) > 2 else None
st = json.load(open(f'{D}/scrimloop.json'))
idx = json.load(open(f'{OUT}/index.json')) if os.path.exists(f'{OUT}/index.json') else {}
for g in st['groups']:
    if not g.get('done'): continue
    for x in g['games']:
        if x['map'] in maps:
            idx[x['id']] = {'map': x['map'], 'side': x['side'], 'result': x['result'], 'opp': g['opp'], 'at': g['at'], 'v16m': True,
                            'rank': g['rank'], 'bot': g.get('bot', '?')}
for mid, v in idx.items():
    if v['map'] not in maps: continue
    js = f'{OUT}/{mid}.json'
    if os.path.exists(js) or not os.path.exists(f'{D}/bundles_scrim/{mid}.zip'): continue
    d = f'{OUT}/{mid}'; os.makedirs(d, exist_ok=True); zipfile.ZipFile(f'{D}/bundles_scrim/{mid}.zip').extractall(d)
    subprocess.run(['node', '/home/claude/tools/replay/extract.mjs', f'{D}/vis/assets', f'{d}/replay.repl26a', js], capture_output=True)
json.dump(idx, open(f'{OUT}/index.json', 'w'), indent=0)
bots = want or sorted({v['bot'] for v in idx.values() if v['map'] in maps})
ms = open('/home/claude/tools/audit/mapstudy.py').read().replace('/home/claude/data/our_rep', '/home/claude/data/scrim_bv')
for b in bots:
    sub = {k: v for k, v in idx.items() if v['map'] in maps and v['bot'] == b and os.path.exists(f'{OUT}/{k}.json')}
    bv = f'{D}/scrim_bv'
    if os.path.islink(bv) or os.path.exists(bv): subprocess.run(['rm', '-rf', bv])
    os.makedirs(bv)
    for k in sub:
        os.symlink(f'{OUT}/{k}.json', f'{bv}/{k}.json'); os.symlink(f'{OUT}/{k}', f'{bv}/{k}')
    json.dump(sub, open(f'{bv}/index.json', 'w'))
    for m in maps:
        if not any(v['map'] == m for v in sub.values()): continue
        r = subprocess.run(['python3', '-I', '-c', ms, m], capture_output=True, text=True)
        print(f'===== {b} {m}'); print('\n'.join(l for l in r.stdout.split('\n') if 'opp drafts' not in l))
    # death causes
    au = open('/home/claude/tools/audit/audit.py').read().replace('/home/claude/data/our_rep', bv)
    r = subprocess.run(['python3', '-I', '-c', au], capture_output=True, text=True, cwd='/home/claude')
    for l in r.stdout.split('\n'):
        if '%)' in l or 'our deaths' in l: print('   ', l.strip())
