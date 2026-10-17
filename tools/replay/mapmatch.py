"""Match replays to ladder maps (the map bytes are embedded in the replay). usage: mapmatch.py <replays_dir> <json_dir>
Expects <replays_dir>/<match-id>/replay.repl26a; writes <json_dir>/maps.json as {match-id: [map name]}."""
import sys, glob, os, json

NAMES = {'25d8': 'rows', '2e98': 'collision', '3991': 'monolith', '3a5c': 'contest', '3e2d': 'eight', '699c': 'ambush',
         '7bfc': 'pilgrimage', '8192': 'expanse', '9385': 'lanes', '9925': 'fragment', 'b135': 'packs', 'b777': 'interlock',
         'bb12': 'elkring', 'df22': 'rushbait_v2', 'e3c2': 'corners', 'f2b6': 'stampede', 'f930': 'swirl'}
MAPS = os.path.join(os.path.dirname(__file__), '..', '..', 'maps')
maps = {os.path.basename(f)[2:6]: open(f, 'rb').read() for f in glob.glob(os.path.join(MAPS, '*.map26a'))}
out = {}
for d in sorted(glob.glob(os.path.join(sys.argv[1], '*/'))):
    r = open(os.path.join(d, 'replay.repl26a'), 'rb').read()
    out[os.path.basename(d.rstrip('/'))] = [NAMES.get(k, k) for k, m in maps.items() if m[8:200] in r] or ['unknown']
json.dump(out, open(os.path.join(sys.argv[2], 'maps.json'), 'w'), indent=1)
for k, v in out.items(): print(k, v)
