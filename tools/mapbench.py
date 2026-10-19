"""Per-map local bench: wins and mean gem margin per map for each candidate vs a set of opponents.
usage: MAPS=p_..,p_.. mapbench.py CAND1,CAND2 OPP1,OPP2,..."""
import sys, os, json, glob, collections, importlib.util
spec = importlib.util.spec_from_file_location('bench', '/home/claude/tools/bench.py'); B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
NAMES = {}
for q in json.load(open('/home/claude/data/maps_index.json')) if os.path.exists('/home/claude/data/maps_index.json') else []:
    NAMES['p_' + q['id'][:8]] = q['name']
cands = sys.argv[1].split(','); opps = sys.argv[2].split(',')
for c in cands:
    agg = collections.defaultdict(lambda: [0, 0, 0.0])
    for o in opps:
        if o == c: continue
        out_before = set(glob.glob(f'/home/claude/data/bench_{c}_vs_{o}_*'))
        B.run(c, o)
        d = sorted(set(glob.glob(f'/home/claude/data/bench_{c}_vs_{o}_*')) - out_before)[-1]
        for p in glob.glob(d + '/*.json'):
            j = json.load(open(p)); tag = os.path.basename(p)[:-5]
            m = tag.split('_')[0] + '_' + tag.split('_')[1]
            rest = tag[len(m) + 1:]
            side = 'teamA' if rest.startswith(c + '_') else 'teamB'
            gems = {t['team']: int(t['submittedGems']) for t in j['teams']}
            a = agg[m]; a[0] += j['match']['outcome'] == side; a[1] += 1; a[2] += gems[side] - gems['teamB' if side == 'teamA' else 'teamA']
    print(c, '  '.join(f"{NAMES.get(m, m)} {w}/{n} ({mg / max(1, n):+.0f})" for m, (w, n, mg) in sorted(agg.items())), flush=True)
