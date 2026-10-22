"""T3 (#40): download and decode our ranked games on chosen maps since a date. Portable (no /home/claude paths).
usage: python tools/t3fetch.py OUTDIR SINCE MAPNAME [MAPNAME ...]     e.g. OUTDIR 2026-10-21T15:24 00contest 00rows
Writes OUTDIR/index.json (one row per match: id, map, side, result, opponent, engine, draft) and OUTDIR/<id>.json decodes.
Decoding uses tools/replay/extract3.mjs with the newest cambc visualiser assets that contain the replay's engine wasm."""
import glob, json, os, re, subprocess, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT, SINCE, MAPS = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(OUT, exist_ok=True)

def cambc(*args):
    r = subprocess.run(['cambc', *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.stdout

def map_ids():
    ids = {}
    for page in (1, 2, 3):
        for line in cambc('maps', 'list', '--page', str(page), '--limit', '25').splitlines():
            m = re.match(r'^([0-9a-f-]{36})\s+(\S+)', line)
            if m: ids[m.group(2)] = m.group(1)
    return ids

def list_matches(map_id):
    rows, cursor = [], None
    while True:
        args = ['matches', 'list', '--team', 'me', '--kind', 'ranked', '--map', map_id, '--limit', '50', '--json']
        if cursor: args += ['--cursor', cursor]
        d = json.loads(cambc(*args) or '{}')
        batch = d.get('matches', [])
        rows += batch
        cursor = d.get('nextCursor') or d.get('cursor')
        if not batch or not cursor or min(m['createdAt'] for m in batch) < SINCE: break
    return [m for m in rows if m['createdAt'] >= SINCE and m.get('status') == 'finished']

def assets_for(engine):
    """Newest visualiser assets folder that has this engine's wasm (v1_0_3-*.wasm) and the decoder's PanelChrome file."""
    tag = 'v' + engine.replace('.', '_')
    cands = []
    for d in glob.glob(os.path.join(os.environ['LOCALAPPDATA'], 'cambc', 'assets', '*', 'visualiser', 'assets')):
        if glob.glob(os.path.join(d, tag + '-*.wasm')) or os.path.exists(os.path.join(d, tag + '.wasm')):
            cands.append((os.path.getmtime(d), d))
    return max(cands)[1] if cands else None

def main():
    ids = map_ids(); index = []
    for name in MAPS:
        for m in list_matches(ids[name]):
            us = next(t for t in m['teams'] if t['name'] == 'LionelMSISS'); them = next(t for t in m['teams'] if t is not us)
            row = {'id': m['matchId'], 'map': name, 'created': m['createdAt'], 'side': us['side'], 'team': 0 if us['side'] == 'a' else 1,
                   'result': us['result'], 'end': m.get('endReason'), 'opponent': them['name'], 'engine': us.get('engineVersion'),
                   'our_draft': us.get('draftPicks'), 'their_draft': them.get('draftPicks'), 'decoded': False}
            js = os.path.join(OUT, row['id'] + '.json')
            if not os.path.exists(js):
                zp = os.path.join(OUT, row['id'] + '.zip')
                if not os.path.exists(zp): cambc('matches', 'download', row['id'], '-o', zp)
                rp = os.path.join(OUT, row['id'] + '.repl26a')
                try:
                    with zipfile.ZipFile(zp) as z:
                        name_in = next(n for n in z.namelist() if n.endswith('.repl26a'))
                        open(rp, 'wb').write(z.read(name_in))
                except Exception:
                    if os.path.exists(zp) and not zipfile.is_zipfile(zp): os.replace(zp, rp)   # a bare replay, not a bundle
                a = assets_for(row['engine'] or '')
                if a and os.path.exists(rp):
                    subprocess.run(['node', os.path.join(ROOT, 'tools', 'replay', 'extract3.mjs'), a, rp, js], capture_output=True)
                elif not a:
                    row['note'] = f"no visualiser assets for engine {row['engine']}"
            row['decoded'] = os.path.exists(js)
            index.append(row)
    json.dump(index, open(os.path.join(OUT, 'index.json'), 'w'), indent=1)
    for name in MAPS:
        rs = [r for r in index if r['map'] == name]
        print(f"{name}: {len(rs)} ranked games since {SINCE}; wins {sum(r['result'] == 'win' for r in rs)}; decoded {sum(r['decoded'] for r in rs)}"
              + (f"; engines {sorted({r['engine'] for r in rs})}" if rs else ''))
    notes = {r.get('note') for r in index if r.get('note')}
    for n in notes: print('NOTE:', n)

if __name__ == '__main__':
    main()
