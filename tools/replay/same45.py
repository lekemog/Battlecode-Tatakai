"""#45 regression screen: are two bots' games identical, map by map?

usage: python3 -I tools/replay/same45.py <dir> <botA> <botB>
Bundles are named <bot>__<map>__<A|B>.repl26a (zip bundles from cambc run-batch). The game record
(replay.repl26a inside each bundle) is compared byte for byte; bot stdout/fuel logs are ignored.
For differing games it also prints both bots' submitted gems at the end of the run."""
import hashlib, json, os, sys, zipfile, collections

d, a, b = sys.argv[1], sys.argv[2], sys.argv[3]


def game(bot, m, side):
    p = os.path.join(d, f'{bot}__{m}__{side}.repl26a')
    if not os.path.exists(p):
        return None, None
    with zipfile.ZipFile(p) as z:
        h = hashlib.sha256(z.read('replay.repl26a')).hexdigest()
    s = os.path.join(d, f'{bot}__{m}__{side}.json')
    gems = None
    if os.path.exists(s):
        j = json.load(open(s))
        me = 'teamA' if side == 'A' else 'teamB'
        gems = {('us' if t['team'] == me else 'them'): int(t['submittedGems']) for t in j['teams']}
    return h, gems


maps = sorted({f.split('__')[1] for f in os.listdir(d) if f.endswith('.repl26a') and f.count('__') == 2})
same, diff, missing = 0, [], 0
for m in maps:
    for side in 'AB':
        ha, ga = game(a, m, side)
        hb, gb = game(b, m, side)
        if ha is None or hb is None:
            missing += 1
        elif ha == hb:
            same += 1
        else:
            diff.append((m, side, ga, gb))
print(f'{len(maps)} maps x 2 sides: identical {same}, different {len(diff)}, missing {missing}')
for m, side, ga, gb in diff:
    print(f'  {m:24s} {side}  {a}: {ga}  {b}: {gb}')
