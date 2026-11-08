"""profreport.py DIR : summarise profsweep.sh output (bots/v51p profiler lines) into decision-efficiency tables.

Reads the last P/G/L/D line of each champion kind per game (cumulative up to that print) and weights by turns.
Tables: fuel per turn by phase; turns and fuel by decision (mode/why); fuel gates that deferred work; decision latency.
"""
import collections
import glob
import os
import re
import statistics
import sys

KIND = {0: 'Ryth', 1: 'Vesper', 2: 'Vendetta', 3: 'Cassi', 4: 'Issac', 5: 'Stellar', 6: 'Prism', 7: 'Marcella', 8: 'Willow', 9: 'Ren', 10: 'Varg', 11: 'Tavi', 12: 'Heart'}


def parse(path):
    """-> {kind: {'P':..., 'G':..., 'L':..., 'D':...}} of the last print of each kind; plus field-cost misses."""
    last = {}
    miss = []
    for line in open(path, errors='replace'):
        m = re.match(r'^([PGLD]) r(\d+) k(\d+)\s*(.*)$', line.rstrip())
        if m:
            t, r, k, rest = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
            cur = last.setdefault(k, {})
            if cur.get('r', -1) <= r:
                if cur.get('r', -1) < r:
                    cur.clear()
                cur['r'] = r
                cur[t] = rest
            continue
        m = re.match(r'^field cost (\d+) exceeded estimate (\d+)', line)
        if m:
            miss.append((int(m.group(1)), int(m.group(2))))
    return last, miss


def main():
    d = sys.argv[1]
    files = sorted(glob.glob(os.path.join(d, '*.prof')))
    turns = tot = 0
    heavy = susp = early = 0
    fuel_max = 0
    start_min = 1 << 60
    phase = collections.defaultdict(lambda: [0.0, 0])      # sum(avg*turns), max
    dec = collections.defaultdict(lambda: [0, 0.0, 0])     # turns, fuel sum, max
    gate = collections.defaultdict(lambda: [0, 0])
    lat = collections.defaultdict(lambda: collections.defaultdict(list))
    bag = collections.Counter()
    missed = []
    games = 0
    for f in files:
        last, miss = parse(f)
        missed += miss
        if not last:
            continue
        games += 1
        for k, e in last.items():
            if 'P' not in e:
                continue
            p = e['P']
            m = re.match(r'turns (\d+) fuel avg (\d+) max (\d+) start_avg (\d+) start_min (\d+) heavy60k (\d+) susp (\d+) early (\d+) \|(.*)', p)
            if not m:
                continue
            n, avg, mx, _sa, smin, hv, sp, ea = map(int, m.groups()[:8])
            turns += n; tot += avg * n; heavy += hv; susp += sp; early += ea
            fuel_max = max(fuel_max, mx); start_min = min(start_min, smin)
            for name, a, x in re.findall(r'(\w+)=(\d+)/(\d+)', m.group(9)):
                phase[name][0] += int(a) * n; phase[name][1] = max(phase[name][1], int(x))
            for mode, why, c, a, x in re.findall(r'([\w-]+)/([\w-]+):(\d+):(\d+):(\d+)', e.get('D', '')):
                key = f'{mode}/{why}'
                dec[key][0] += int(c); dec[key][1] += int(c) * int(a); dec[key][2] = max(dec[key][2], int(x))
            for name, df, ck in re.findall(r'(\w+)=(\d+)/(\d+)', e.get('G', '')):
                gate[name][0] += int(df); gate[name][1] += int(ck)
            g = re.match(r'first_off (-?\d+) first_fight (-?\d+) first_capture (-?\d+) first_bank (-?\d+) bag_turns (\d+) bag_wait (\d+) \(pvp (\d+) farm (\d+)\) bag_gems_wait (\d+) lowhp_turns (\d+) lowhp_wait (\d+) \(fight (\d+) travel (\d+)\)', e.get('L', ''))
            if g:
                fo, ff, fc, fb, bt, bw, bp, bf, bgw, lt, lw, lwf, lwt = map(int, g.groups())
                for name, v in (('first_off', fo), ('first_fight', ff), ('first_capture', fc), ('first_bank', fb)):
                    if v >= 0:
                        lat[KIND.get(k, k)][name].append(v)
                bag['bag_turns'] += bt; bag['bag_wait'] += bw; bag['bag_pvp'] += bp; bag['bag_farm'] += bf
                bag['bag_gems_wait'] += bgw; bag['lowhp_turns'] += lt; bag['lowhp_wait'] += lw; bag['lowhp_fight'] += lwf; bag['lowhp_travel'] += lwt
    bymap = collections.defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0])  # turns, fuel, heavy, idle-none turns, field deferred, field reached, susp
    for f in files:
        last, _ = parse(f)
        m = os.path.basename(f).split('_')[0]
        for k, e in last.items():
            q = re.match(r'turns (\d+) fuel avg (\d+) max (\d+) start_avg (\d+) start_min (\d+) heavy60k (\d+) susp (\d+)', e.get('P', ''))
            if not q:
                continue
            n, avg, _mx, _sa, _sm, hv, sp = map(int, q.groups())
            b = bymap[m]; b[0] += n; b[1] += avg * n; b[2] += hv; b[6] += sp
            for mode, why, c, a, x in re.findall(r'([\w-]+)/([\w-]+):(\d+):(\d+):(\d+)', e.get('D', '')):
                if mode == 'idle' and why == 'idle-none':
                    b[3] += int(c)
            for name, df, ck in re.findall(r'(\w+)=(\d+)/(\d+)', e.get('G', '')):
                if name == 'field':
                    b[4] += int(df); b[5] += int(ck)
    print('Per map: fuel/turn, turns >60K, idle-none turns, field gate deferred, suspended')
    for m, b in sorted(bymap.items(), key=lambda kv: -kv[1][1] / max(1, kv[1][0])):
        print(f'  {m:14s} {b[1] / b[0]:7.0f}  {100 * b[2] / b[0]:5.1f}%  {100 * b[3] / b[0]:5.1f}%  {100 * b[4] / max(1, b[5]):5.1f}%  {b[6]}')
    print()
    print(f'{games} games, {turns} champion-turns profiled')
    print(f'fuel/turn avg {tot / turns:.0f}  max {fuel_max}  lowest start-of-turn fuel {start_min}  turns >60K: {heavy} ({100 * heavy / turns:.2f}%)  suspended: {susp}  early-return turns: {early} ({100 * early / turns:.1f}%)')
    print('\nFuel per turn by phase (avg over all turns, worst single turn):')
    for name, (s, mx) in sorted(phase.items(), key=lambda kv: -kv[1][0]):
        print(f'  {name:8s} {s / turns:8.0f}  ({100 * s / tot:4.1f}%)  worst {mx}')
    print('\nDecisions (mode/why): share of turns, avg fuel per turn, worst turn:')
    for key, (c, s, mx) in sorted(dec.items(), key=lambda kv: -kv[1][0])[:22]:
        print(f'  {key:22s} {100 * c / turns:5.1f}%  {s / c:8.0f}  worst {mx}')
    print('\nFuel gates (deferred / reached):')
    for name, (df, ck) in sorted(gate.items()):
        print(f'  {name:8s} {df:6d} / {ck:6d}  ({100 * df / max(1, ck):.2f}% deferred)')
    print('\nDecision latency:')
    for kind in sorted(lat):
        row = lat[kind]
        print('  %-9s ' % kind + '  '.join(f'{n} med {statistics.median(v):.0f} (n={len(v)})' for n, v in sorted(row.items())))
    if bag['bag_turns']:
        print(f"  bag at/above bank threshold: {bag['bag_turns']} turns, {100 * bag['bag_wait'] / bag['bag_turns']:.1f}% not banking (of which in a fight {100 * bag['bag_pvp'] / max(1, bag['bag_wait']):.0f}%, farming/capturing {100 * bag['bag_farm'] / max(1, bag['bag_wait']):.0f}%); mean gems waiting {bag['bag_gems_wait'] / max(1, bag['bag_wait']):.0f}")
    if bag['lowhp_turns']:
        print(f"  low health (<recall threshold) off spawn: {bag['lowhp_turns']} turns, {100 * bag['lowhp_wait'] / bag['lowhp_turns']:.1f}% not yet healing or in a player fight (of those: camp fight/capture {100 * bag['lowhp_fight'] / max(1, bag['lowhp_wait']):.0f}%, travelling {100 * bag['lowhp_travel'] / max(1, bag['lowhp_wait']):.0f}%)")
    if missed:
        ratio = [a / b for a, b in missed]
        print(f'\nField-cost model misses: {len(missed)} logged; actual/estimate median {statistics.median(ratio):.2f}, p90 {sorted(ratio)[int(0.9 * len(ratio))]:.2f}, max {max(ratio):.2f}')


if __name__ == '__main__':
    main()
