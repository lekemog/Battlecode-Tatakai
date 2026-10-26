"""Light A/B behaviour metrics from scrim bundles: decode, extract, delete. No large files kept.
usage: abbehav.py MAPS BOTS [N]   e.g. abbehav.py contest,eight v19n,v20k 15
Per (bot,map): wins, our/their max HP @r300, deaths, gems @r400 (submitted), first-death round, gold earned @r300."""
import json, os, sys, zipfile, subprocess, statistics as st, tempfile, shutil
D = '/home/claude/data'; maps = sys.argv[1].split(','); bots = sys.argv[2].split(','); N = int(sys.argv[3]) if len(sys.argv) > 3 else 15
S = json.load(open(f'{D}/scrimloop.json'))
CACHE = f'{D}/abbehav_cache.json'; cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
for b in bots:
    for m in maps:
        games = [(g, x) for g in S['groups'] if g.get('done') and g.get('bot') == b and (b != 'v19n' or g['at'] >= '2026-10-19T06:40') for x in g['games'] if x['map'] == m][-N:]
        rows = []
        for g, x in games:
            mid = x['id']
            if mid not in cache:
                z = f'{D}/bundles_scrim/{mid}.zip'
                if not os.path.exists(z): continue
                tmp = tempfile.mkdtemp(dir=f'{D}'); zipfile.ZipFile(z).extractall(tmp); js = f'{tmp}/r.json'
                subprocess.run(['node', '/home/claude/tools/replay/extract.mjs', f'{D}/vis/assets', f'{tmp}/replay.repl26a', js], capture_output=True)
                try:
                    R = json.load(open(js))['rounds']; us = 0 if x['side'] == 'a' else 1
                    def team(t, tm): return [c for c in R[min(t, len(R) - 1)]['champions'] if c['team'] == tm]
                    dead = [0, 0]; first = None; prev = {c['entity']['index']: c.get('alive') for c in R[10]['champions']}
                    for t in range(11, len(R)):
                        for c in R[t]['champions']:
                            i = c['entity']['index']
                            if prev.get(i) and not c.get('alive'):
                                w = 0 if c['team'] == us else 1; dead[w] += 1
                                if w == 0 and first is None: first = t
                            prev[i] = c.get('alive')
                    cache[mid] = {'win': x['result'] == 'win', 'hp': [st.mean(c['maxHealth'] for c in team(300, tm)) for tm in (us, 1 - us)],
                                  'deaths': dead, 'g400': [R[min(400, len(R) - 1)]['submittedGems'][tm] for tm in (us, 1 - us)],
                                  'gold300': [st.mean(c.get('earnedGold', 0) for c in team(300, tm)) for tm in (us, 1 - us)], 'first': first or len(R), 'rounds': len(R)}
                except Exception as e:
                    pass
                shutil.rmtree(tmp, ignore_errors=True)
                json.dump(cache, open(CACHE, 'w'))
            if mid in cache: rows.append(cache[mid])
        if not rows: print(b, m, 'no games'); continue
        f = lambda k, i: st.mean(r[k][i] for r in rows)
        print(f"{b:5} {m:9} n={len(rows):2} wins {sum(r['win'] for r in rows):2} | HP@300 {f('hp',0):.0f}/{f('hp',1):.0f} | deaths {f('deaths',0):.1f}/{f('deaths',1):.1f} | "
              f"gems@400 {f('g400',0):.0f}/{f('g400',1):.0f} | gold@300 {f('gold300',0):.0f}/{f('gold300',1):.0f} | first death r{st.median(r['first'] for r in rows):.0f}", flush=True)
