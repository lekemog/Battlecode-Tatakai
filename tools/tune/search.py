"""search.py BASE [--stage1 64] [--top 3] [--live v50h5e] : black-box tuning of config.h knobs by local games.

Stage 1 (screen): for each (knob, value) in SPACE, a copy of $PROJ/bots/BASE with that one value changed plays BASE on a fixed
random subset of maps (both sides). Stage 2 (confirm): the best --top variants by win share play BASE on all maps and the live
bot on all maps. Results are appended to $PROJ/tune_<BASE>.tsv (variant, knob, value, stage, opponent, wins, games, margin).
Noise: about +-6 wins at 128 games, +-8 at 256; only confirmed gains count.
"""
import os
import random
import re
import shutil
import subprocess
import sys

PROJ = os.path.expanduser(os.environ.get('PROJ', '~/lab'))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPACE = [
    ('fight_margin', ['0.3f', '0.7f']),
    ('behind_fight_margin', ['0.7f', '1.3f']),
    ('hazard_threshold', ['0.15f', '0.25f']),
    ('hazard_commit', ['2', '5']),
    ('escort_until', ['60', '150']),
    ('pack_size', ['2', '4']),
    ('tribute_gems_danger', ['15', '30']),
    ('retarget_ratio', ['1.2f', '1.5f']),
    ('approach_margin', ['0.25f']),
]


def make_variant(base, knob, value):
    name = f't{abs(hash((base, knob, value))) % 10**6:06d}'
    dst = os.path.join(PROJ, 'bots', name)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(os.path.join(PROJ, 'bots', base), dst, ignore=shutil.ignore_patterns('.cambc'))
    p = os.path.join(dst, 'src', 'config.h')
    s = open(p).read()
    pat = re.compile(r'(inline constexpr (?:float|int|bool) ' + re.escape(knob) + r' = )([^;]+);')
    if not pat.search(s):
        raise SystemExit(f'knob {knob} not in {p}')
    s = pat.sub(lambda m: m.group(1) + value + ';', s, count=1)
    open(p, 'w').write(s)
    return name


def mirror(cand, base, maplist):
    env = dict(os.environ, PROJ=PROJ, MAPLIST=maplist, JOBS=os.environ.get('JOBS', '4'))
    out = subprocess.run([os.path.join(REPO, 'tools', 'lab', 'mirror.sh'), cand, base], capture_output=True, text=True, env=env).stdout
    m = re.search(r'games (\d+) cand wins (\d+) base wins (\d+).*mean gem margin ([+-]?\d+)', out)
    if not m:
        return None
    return int(m.group(2)), int(m.group(1)), int(m.group(4))


def main():
    base = sys.argv[1]
    args = sys.argv[2:]
    n1 = int(args[args.index('--stage1') + 1]) if '--stage1' in args else 64
    top = int(args[args.index('--top') + 1]) if '--top' in args else 3
    live = args[args.index('--live') + 1] if '--live' in args else 'v50h5e'
    allmaps = [l.strip() for l in open(os.path.join(PROJ, 'all.txt')) if l.strip()]
    random.seed(7)
    sub = sorted(random.sample(allmaps, min(n1, len(allmaps))))
    subf = os.path.join(PROJ, f'tune_maps_{n1}.txt')
    open(subf, 'w').write('\n'.join(sub) + '\n')
    logp = os.path.join(PROJ, f'tune_{base}.tsv')
    done = {}
    if os.path.exists(logp):
        for line in open(logp):
            p = line.rstrip('\n').split('\t')
            if len(p) == 8 and p[3] == '1' and int(p[6]) > 0:
                done[(p[1], p[2])] = (int(p[5]) / int(p[6]), int(p[7]), p[0])
    log = open(logp, 'a')
    res = [(sh, mg, name, k, v) for (k, v), (sh, mg, name) in done.items()]
    for knob, values in SPACE:
        for v in values:
            if (knob, v) in done:
                continue
            name = make_variant(base, knob, v)
            r = mirror(name, base, subf)
            if r is None:
                print('failed', knob, v, flush=True)
                continue
            w, g, mg = r
            if g == 0:
                print('no games', knob, v, flush=True)
                continue
            print(f'stage1 {knob}={v}: {w}/{g} margin {mg:+d}', flush=True)
            log.write(f'{name}\t{knob}\t{v}\t1\t{base}\t{w}\t{g}\t{mg}\n'); log.flush()
            res.append((w / g, mg, name, knob, v))
    res.sort(reverse=True)
    full = os.path.join(PROJ, 'all.txt')
    for share, mg, name, knob, v in res[:top]:
        for opp in (base, live):
            r = mirror(name, opp, full)
            if r is None:
                continue
            w, g, m2 = r
            print(f'stage2 {knob}={v} vs {opp}: {w}/{g} margin {m2:+d}', flush=True)
            log.write(f'{name}\t{knob}\t{v}\t2\t{opp}\t{w}\t{g}\t{m2}\n'); log.flush()


if __name__ == '__main__':
    main()
