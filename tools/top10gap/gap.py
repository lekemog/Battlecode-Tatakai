"""gap.py LABEL [LABEL ...] : us-vs-them gap report from a stored panel (results/panel/LABEL.json + summaries/*.json.gz).

Prints per label: team gold / gems curves at r25-r500, kills, deaths and damage totals, death timing and context,
where deaths and camp clears happen (own third / middle / enemy third, by distance to each team's shop tile),
death clustering (deaths of ours within 10 rounds of each other), per-champion lines for both teams, consumables,
and a per-opponent table. Read-only; uses only the official match summaries. Written 10 Nov 2026 (top-10 gap study).

The 'home' tile of a team is the most common position of its buyItem/buyConsumable events (shopping happens on spawn).
"""
import collections
import gzip
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = os.path.join(REPO, "results", "panel")


def tl_at(runs, r):
    t = 0
    v = 0.0
    for x in runs:
        if t > r:
            break
        v = float(x["value"])
        t += x["duration"]
    return v


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def load(label):
    d = json.load(open(os.path.join(P, label + ".json")))
    rows = []
    for opp, games in d["games"].items():
        for g in games:
            f = os.path.join(P, "summaries", g["match"] + ".json.gz")
            if not os.path.exists(f):
                continue
            s = json.load(gzip.open(f))
            us = "teamA" if g["side"] == "a" else "teamB"
            th = "teamB" if us == "teamA" else "teamA"
            r = {"opp": opp.rsplit("-", 1)[0], "map": g["map"], "win": g["win"], "team": {"u": us, "t": th}}
            for side, t in (("u", us), ("t", th)):
                r[side] = side_stats(s, t)
            home = {k: r[k]["home"] for k in "ut"}
            for side, o in (("u", "t"), ("t", "u")):
                zones = collections.Counter()
                czones = collections.Counter()
                for kind, key in (("death", zones), ("campClear", czones)):
                    for rd, en, _ in r[side]["ev"][kind]:
                        if home[side] is None or home[o] is None:
                            continue
                        p = (en["x"], en["y"])
                        a, b = cheb(p, home[side]), cheb(p, home[o])
                        f = a / (a + b + 1e-9)
                        key["own" if f < 0.4 else "mid" if f < 0.6 else "enemy"] += 1
                r[side]["death_zone"] = zones
                r[side]["clear_zone"] = czones
            rows.append(r)
    return rows


def side_stats(s, t):
    out = {"curve": {}}
    for rr in (25, 50, 100, 200, 300, 500):
        for metric, key in (("earnedGold", "g"), ("collectedGems", "cg"), ("submittedGems", "sg")):
            out["curve"][(key, rr)] = sum(
                tl_at(x["runs"], rr) for x in s["championTimelines"] if x["metric"] == metric and x["owner"]["team"] == t
            )
    ev = collections.defaultdict(list)
    for e in s["events"]:
        if e["owner"].get("team") == t:
            for en in e["entries"]:
                ev[e["kind"]].append((en["timestamp"]["round"], en, e["owner"]["name"]))
    out["ev"] = ev
    ch = [c for c in s["champions"] if c["team"] == t]
    out["tot"] = collections.Counter()
    out["champ"] = {}
    for c in ch:
        m = {k: float(v) for k, v in c["metrics"].items()}
        out["champ"][c["name"]] = m
        out["tot"].update(m)
    pos = collections.Counter((en["x"], en["y"]) for k in ("buyItem", "buyConsumable") for _, en, _ in ev[k])
    out["home"] = pos.most_common(1)[0][0] if pos else None
    return out


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def report(label):
    rows = load(label)
    n = len(rows)
    print(f"=== {label}: {n} games, {sum(r['win'] for r in rows)} wins")
    print("team curves (us / them): earned gold, collected gems, banked gems")
    for rr in (25, 50, 100, 200, 300, 500):
        c = lambda side, k: mean(r[side]["curve"][(k, rr)] for r in rows)
        print(f"  r{rr:<3} gold {c('u','g'):6.0f} / {c('t','g'):6.0f}   collected {c('u','cg'):5.0f} / {c('t','cg'):5.0f}   banked {c('u','sg'):5.0f} / {c('t','sg'):5.0f}")
    print(f"  ahead on gold at r200 in {sum(r['u']['curve'][('g',200)] > r['t']['curve'][('g',200)] for r in rows)} of {n}")
    for k in ("kills", "deaths", "assists", "earnedGold", "collectedGems", "submittedGems", "monsterDamageDone",
              "championDamageDone", "healingDone", "shieldingDone"):
        print(f"  {k:20} us {mean(r['u']['tot'][k] for r in rows):9.1f}   them {mean(r['t']['tot'][k] for r in rows):9.1f}")
    for side, name in (("u", "our"), ("t", "their")):
        ds = [x for r in rows for x in r[side]["ev"]["death"]]
        bins = collections.Counter(min(x[0] // 100, 10) for x in ds)
        ctx = collections.Counter(x[1]["context"] for x in ds)
        fd = sorted(min(x[0] for x in r[side]["ev"]["death"]) for r in rows if r[side]["ev"]["death"])
        print(f"  {name} deaths {len(ds)/n:.2f}/game, context {dict(ctx)}, per 100 rounds {[bins.get(i, 0) for i in range(11)]}, "
              f"first-death median r{fd[len(fd)//2] if fd else '-'}")
        dz = sum((r[side]["death_zone"] for r in rows), collections.Counter())
        cz = sum((r[side]["clear_zone"] for r in rows), collections.Counter())
        print(f"    {name} deaths by zone (own frame) {dict(dz)}; camp clears per game by zone "
              f"{ {k: round(v / n, 1) for k, v in cz.items()} }")
        lost = sum(float(x[1]["value"]) for r in rows for x in r[side]["ev"]["gemLoss"]) / n
        cons = collections.Counter(x[1]["target"]["name"] for r in rows for x in r[side]["ev"]["buyConsumable"])
        print(f"    gems lost {lost:.0f}/game; consumables per game { {k: round(v / n, 1) for k, v in cons.items()} }; "
              f"wards {mean(len(r[side]['ev']['wardPlacement']) for r in rows):.0f}/game")
    clusters = collections.Counter()
    for r in rows:
        ds = sorted(x[0] for x in r["u"]["ev"]["death"])
        i = 0
        while i < len(ds):
            j = i
            while j + 1 < len(ds) and ds[j + 1] - ds[i] <= 10:
                j += 1
            clusters[j - i + 1] += 1
            i = j + 1
    print(f"  our deaths grouped within 10 rounds (size: count) {sorted(clusters.items())}")
    killers = collections.Counter(x[1]["target"].get("name") for r in rows for x in r["u"]["ev"]["death"] if x[1]["context"] == "champion")
    print(f"  enemy champions credited with our deaths {killers.most_common(6)}")
    for side, name in (("t", "THEIR"), ("u", "OUR")):
        agg = collections.defaultdict(collections.Counter)
        cnt = collections.Counter()
        for r in rows:
            for nm, m in r[side]["champ"].items():
                cnt[nm] += 1
                agg[nm].update(m)
        print(f"  {name} champions (per game fielded): kills deaths gold collected/banked monster-dmg champ-dmg heal shield")
        for nm in sorted(agg, key=lambda x: -cnt[x]):
            a, c = agg[nm], cnt[nm]
            print(f"    {nm:14} n={c:2} K {a['kills']/c:4.1f} D {a['deaths']/c:4.1f} gold {a['earnedGold']/c:5.0f} "
                  f"gems {a['collectedGems']/c:4.0f}/{a['submittedGems']/c:4.0f} mdmg {a['monsterDamageDone']/c/1000:5.1f}k "
                  f"cdmg {a['championDamageDone']/c/1000:4.1f}k heal {a['healingDone']/c:5.0f} shield {a['shieldingDone']/c:5.0f}")
    by = collections.defaultdict(list)
    for r in rows:
        by[r["opp"]].append(r)
    print("  per opponent: wins, gold r200 us/them, deaths us/them, kills us/them, their crystals/game")
    for o, rs in by.items():
        m = lambda f: mean(f(r) for r in rs)
        tc = m(lambda r: sum(1 for x in r["t"]["ev"]["buyConsumable"] if x[1]["target"]["name"] == "Teleport Crystal"))
        print(f"    {o[:24]:24} {sum(r['win'] for r in rs)}/{len(rs)}  {m(lambda r: r['u']['curve'][('g',200)]):5.0f}/{m(lambda r: r['t']['curve'][('g',200)]):5.0f}"
              f"  {m(lambda r: r['u']['tot']['deaths']):4.1f}/{m(lambda r: r['t']['tot']['deaths']):4.1f}"
              f"  {m(lambda r: r['u']['tot']['kills']):3.1f}/{m(lambda r: r['t']['tot']['kills']):4.1f}  {tc:4.1f}")


if __name__ == "__main__":
    for lab in sys.argv[1:] or ["t10b_240"]:
        report(lab)
