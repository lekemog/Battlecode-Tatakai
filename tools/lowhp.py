"""Low-HP episodes (#40 T3 review): how champions recover, for us vs the opponent, in decoded games.
An episode starts when an alive champion off its spawn (>4 tiles from its spawn centroid) drops below 30% max HP
(the live bot's retreat/recall threshold). It ends when the champion dies, or when it is back off spawn with >=90% HP
("resumed"), or after 300 rounds ("open"). Per episode: recall attempts (channelType 1 starts), completed recalls
(channel ended at spawn), cancelled recalls (ended elsewhere, alive), death while recalling, death otherwise, and the
rounds until it resumed. Channel codes from replays: 1 = recall (median 5 rounds), 2 = tribute.
usage: python tools/lowhp.py DIR MAP [FROM_ROUND=150]       (DIR/index.json from tools/t3fetch.py)"""
import json, os, sys, statistics as st

DIR, MAP = sys.argv[1], sys.argv[2]; FROM = int(sys.argv[3]) if len(sys.argv) > 3 else 150
cheb = lambda p, q: max(abs(p['x'] - q[0]), abs(p['y'] - q[1]))

def episodes(path, team):
    d = json.load(open(path, encoding='utf-8'))
    R = {}
    for x in d['rounds']:
        if x['phase'] != 12: R[x['round']] = x
    rs = sorted(R); f = R[rs[0]]
    ps = [c['position'] for c in f['champions'] if c['team'] == team]
    home = (sum(p['x'] for p in ps) / len(ps), sum(p['y'] for p in ps) / len(ps))
    open_ep = {}; done = []; prev = {}
    for r in rs:
        for c in R[r]['champions']:
            if c['team'] != team: continue
            k = c['entity']['index']; pc = prev.get(k); ep = open_ep.get(k)
            pos = c.get('position'); off = pos is not None and cheb(pos, home) > 4
            ct = c.get('channelType', 0) if c['alive'] else 0
            if ep is not None:
                if pc and pc['ct'] == 1 and ct != 1:       # a recall channel ended this round
                    if not c['alive']: pass
                    elif pos is not None and cheb(pos, home) <= 4: ep['recall_done'] += 1
                    else: ep['recall_cancel'] += 1
                if ct == 1 and (not pc or pc['ct'] != 1): ep['recall_try'] += 1
                if not c['alive']:
                    ep['end'] = 'death_recalling' if pc and pc['ct'] == 1 else 'death'; ep['len'] = r - ep['start']
                    done.append(ep); del open_ep[k]
                elif off and c['health'] >= .9 * c['maxHealth']:
                    ep['end'] = 'resumed'; ep['len'] = r - ep['start']; done.append(ep); del open_ep[k]
                elif r - ep['start'] > 300:
                    ep['end'] = 'open'; ep['len'] = r - ep['start']; done.append(ep); del open_ep[k]
            elif c['alive'] and off and r >= FROM and c['health'] < .3 * c['maxHealth']:
                open_ep[k] = {'start': r, 'recall_try': 0, 'recall_done': 0, 'recall_cancel': 0, 'late': r > 600}
                if ct == 1: open_ep[k]['recall_try'] = 1
            prev[k] = {'ct': ct}
    return done

def summary(eps, label):
    n = len(eps)
    if not n: print(f'  {label}: no episodes'); return
    tries = sum(e['recall_try'] for e in eps); done = sum(e['recall_done'] for e in eps); canc = sum(e['recall_cancel'] for e in eps)
    dr = sum(e['end'] == 'death_recalling' for e in eps); dn = sum(e['end'] == 'death' for e in eps); res = [e for e in eps if e['end'] == 'resumed']
    with_try = [e for e in eps if e['recall_try']]; no_try = [e for e in eps if not e['recall_try']]
    died = lambda es: sum(e['end'].startswith('death') for e in es) / max(1, len(es))
    print(f"  {label}: {n} episodes | died {(dr + dn) / n:.0%} (while recalling {dr}, otherwise {dn}) | resumed {len(res) / n:.0%}"
          f" in median {st.median(e['len'] for e in res) if res else float('nan'):.0f} rounds")
    print(f"      recall attempts {tries} ({tries / n:.2f}/episode): completed {done} ({done / max(1, tries):.0%}), cancelled {canc} ({canc / max(1, tries):.0%}),"
          f" death while recalling {dr} ({dr / max(1, tries):.0%} of attempts)")
    print(f"      episodes with a recall attempt: {len(with_try)}, died {died(with_try):.0%} | without: {len(no_try)}, died {died(no_try):.0%}")

def main():
    # utf-8-sig: index files written by Windows PowerShell 5.1 carry a byte-order mark.
    idx = [r for r in json.load(open(os.path.join(DIR, 'index.json'), encoding='utf-8-sig')) if r['map'] == MAP and r['decoded']]
    us, them = [], []
    for g in idx:
        p = os.path.join(DIR, g['id'] + '.json')
        us += episodes(p, g['team']); them += episodes(p, 1 - g['team'])
    print(f'=== {MAP}: low-HP episodes from r{FROM}, {len(idx)} games ===')
    for lab, sel in (('r150-600', lambda e: not e['late']), ('r600+', lambda e: e['late'])):
        print(f'-- {lab} --')
        summary([e for e in us if sel(e)], 'us  ')
        summary([e for e in them if sel(e)], 'them')

if __name__ == '__main__':
    main()
